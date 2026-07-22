"""Pipeline reproduzível das bases territoriais da Comunidade do Pilar.

Camadas geradas:
  Fontes_Summerjob/       dados brutos preservados
  dados/02_tratados/     tabelas normalizadas em UTF-8
  dados/03_recortes/     recortes territorial e CadÚnico Pilar
  dados/04_indicadores/  indicadores, catálogo e relatório de qualidade
"""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "Fontes_Summerjob"
TREATED = ROOT / "dados" / "02_tratados"
CUTS = ROOT / "dados" / "03_recortes"
GOLD = ROOT / "dados" / "04_indicadores"
PILAR_BUFFER_METERS = 500

CSV_FILES = {
    "cadunico": "cadastro-unico-2023.csv",
    "bairros_rpa": "bairros-e-rpas-do-recife.csv",
    "pracas": "parques-e-pracas.csv",
    "ciclovias": "detalhes-da-implantacao-da-malha-cicloviaria-do-recife.csv",
    "urbanismo": "urbanismo-tatico-.csv",
    "logradouros": "trechos-de-logradouros-por-bairro.csv",
    "wifi": "localidades-do-conecta-recife-wifi.csv",
}

REQUIRED_COLUMNS = {
    "cadunico": ["cod_familiar", "d.nom_estab_assist_saude_fam", "p.cod_raca_cor_pessoa", "dat_atualizacao"],
    "bairros_rpa": ["Bairro", "rpa"],
    "pracas": ["nome_bairro", "latitude", "longitude", "area"],
    "ciclovias": ["rota", "tipologia", "bairros", "extensao", "inauguracao"],
    "urbanismo": ["bairro", "latitude", "longitude", "ano", "tipo"],
    "logradouros": ["nomeBairro", "desc_indica_pavimentacao"],
    "wifi": ["NOME", "BAIRRO", "LATITUDE", "LONGITUDE"],
}

RACE = {1: "Branca", 2: "Preta", 3: "Amarela", 4: "Parda", 5: "Indígena"}
SEX = {1: "Masculino", 2: "Feminino"}
AGE = {
    0: "0 a 4", 1: "5 a 6", 2: "7 a 15", 3: "16 a 17", 4: "18 a 24",
    5: "25 a 34", 6: "35 a 39", 7: "40 a 44", 8: "45 a 49",
    9: "50 a 54", 10: "55 a 59", 11: "60 a 64", 12: "65 ou mais",
}
EDUCATION = {
    1: "Sem instrução", 2: "Fundamental incompleto", 3: "Fundamental completo",
    4: "Médio incompleto", 5: "Médio completo ou superior",
}
YES_NO = {0: "Não", 1: "Sim", 2: "Não"}


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    return " ".join(text.encode("ascii", "ignore").decode("ascii").upper().split())


def snake(name: str) -> str:
    value = normalize_text(name).lower().replace(".", "_")
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_")


def read_csv_safely(path: Path) -> tuple[pd.DataFrame, str]:
    errors: list[str] = []
    for encoding in ("utf-8-sig", "utf-8", "latin1"):
        try:
            return pd.read_csv(path, sep=None, engine="python", encoding=encoding), encoding
        except (UnicodeDecodeError, pd.errors.ParserError) as exc:
            errors.append(f"{encoding}: {exc}")
    raise ValueError(f"Não foi possível ler {path.name}: {' | '.join(errors)}")


def require_columns(name: str, frame: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS[name] if column not in frame.columns]
    if missing:
        raise ValueError(f"{name}: colunas obrigatórias ausentes: {missing}")


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype("string").str.replace(",", ".", regex=False), errors="coerce")


def point_layer(frame: pd.DataFrame, lon: str, lat: str) -> gpd.GeoDataFrame:
    copy = frame.copy()
    copy[lon] = numeric(copy[lon])
    copy[lat] = numeric(copy[lat])
    valid = copy[lon].between(-35.3, -34.5) & copy[lat].between(-8.3, -7.7)
    copy = copy.loc[valid].copy()
    return gpd.GeoDataFrame(copy, geometry=gpd.points_from_xy(copy[lon], copy[lat]), crs="EPSG:4326")


def add_spatial_classification(points: gpd.GeoDataFrame, pilar: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    points_m = points.to_crs("EPSG:31985")
    pilar_m = pilar.to_crs("EPSG:31985")
    polygon = pilar_m.geometry.union_all()
    buffer = polygon.buffer(PILAR_BUFFER_METERS)
    points_m["recorte_territorial"] = np.select(
        [points_m.geometry.within(polygon), points_m.geometry.within(buffer)],
        ["ZEIS Pilar", f"Entorno até {PILAR_BUFFER_METERS} m"],
        default="Fora do recorte",
    )
    return points_m.to_crs("EPSG:4326")


def quality_row(name: str, frame: pd.DataFrame, encoding: str) -> dict:
    return {
        "base": name,
        "arquivo": CSV_FILES[name],
        "encoding_detectado": encoding,
        "registros": len(frame),
        "colunas": len(frame.columns),
        "linhas_duplicadas": int(frame.duplicated().sum()),
        "celulas_nulas": int(frame.isna().sum().sum()),
        "percentual_celulas_nulas": round(float(frame.isna().mean().mean() * 100), 2),
        "status": "aprovado_com_alertas" if frame.duplicated().any() or frame.isna().any().any() else "aprovado",
    }


def save_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    export = frame.drop(columns="geometry", errors="ignore")
    export.to_csv(path, index=False, encoding="utf-8-sig")


def build_pipeline() -> None:
    for directory in (TREATED, CUTS, GOLD):
        directory.mkdir(parents=True, exist_ok=True)

    tables: dict[str, pd.DataFrame] = {}
    quality: list[dict] = []
    encodings: dict[str, str] = {}
    for name, filename in CSV_FILES.items():
        frame, encoding = read_csv_safely(RAW / filename)
        require_columns(name, frame)
        tables[name] = frame
        encodings[name] = encoding
        quality.append(quality_row(name, frame, encoding))

    # CadÚnico: recorte verificável, sem fallback por posição.
    cad = tables["cadunico"].copy()
    establishment = cad["d.nom_estab_assist_saude_fam"].astype("string")
    cad = cad.loc[establishment.str.contains(r"\bPILAR\b", case=False, na=False)].copy()
    if cad.empty:
        raise ValueError("CadÚnico: nenhum registro da unidade de saúde do Pilar foi encontrado.")
    cad["ano_atualizacao"] = pd.to_datetime(cad["dat_atualizacao"], dayfirst=True, errors="coerce").dt.year.astype("Int64")
    cad["raca_cor"] = numeric(cad["p.cod_raca_cor_pessoa"]).map(RACE).fillna("Não informado")
    cad["sexo"] = numeric(cad["p.cod_sexo_pessoa"]).map(SEX).fillna("Não informado")
    cad["faixa_etaria"] = numeric(cad["p.fx_idade"]).map(AGE).fillna("Não informado")
    cad["escolaridade"] = numeric(cad["p.grau_instrucao"]).map(EDUCATION).fillna("Não informado")
    cad["bolsa_familia"] = numeric(cad["d.marc_pbf"]).map(YES_NO).fillna("Não informado")
    cad["possui_deficiencia"] = numeric(cad["p.cod_deficiencia_memb"]).map({1: "Sim", 2: "Não"}).fillna("Não informado")
    cad["situacao_rua"] = numeric(cad["p.marc_sit_rua"]).map({0: "Não", 1: "Sim"}).fillna("Não informado")
    for column in ["vlr_renda_media", "vlr_renda_total", "d.val_desp_alimentacao_fam"]:
        cad[column] = numeric(cad[column])
    save_csv(cad, CUTS / "cadunico_pilar.csv")

    # Padronizações tabulares preservam colunas originais e acrescentam auxiliares.
    pracas = tables["pracas"].copy()
    pracas["area_m2"] = numeric(pracas["area"])
    pracas["bairro_normalizado"] = pracas["nome_bairro"].map(normalize_text)
    ciclovias = tables["ciclovias"].copy()
    ciclovias["extensao_km"] = numeric(ciclovias["extensao"])
    ciclovias["ano_inauguracao"] = numeric(ciclovias["inauguracao"]).astype("Int64")
    urbanismo = tables["urbanismo"].copy()
    urbanismo["metragem_m"] = numeric(urbanismo["metragem"])
    logradouros = tables["logradouros"].copy()
    logradouros["bairro_normalizado"] = logradouros["nomeBairro"].map(normalize_text)
    wifi = tables["wifi"].copy()
    wifi["bairro_normalizado"] = wifi["BAIRRO"].map(normalize_text)
    bairros = tables["bairros_rpa"].copy()
    bairros["bairro_normalizado"] = bairros["Bairro"].map(normalize_text)

    treated = {"pracas": pracas, "ciclovias": ciclovias, "urbanismo": urbanismo,
               "logradouros": logradouros, "wifi": wifi, "bairros_rpa": bairros}
    for name, frame in treated.items():
        save_csv(frame, TREATED / f"{name}.csv")

    # Polígono da ZEIS Pilar e classificação espacial de bases com coordenadas.
    zeis = gpd.read_file(RAW / "zoneamento-plano-diretor-zeis.geojson")
    if zeis.crs is None:
        zeis = zeis.set_crs("EPSG:4326")
    zeis["AREA_HA"] = numeric(zeis["AREA_HA"])
    pilar = zeis.loc[zeis["NMNOME"].astype("string").str.contains(r"\bPilar\b", case=False, na=False)].copy()
    if pilar.empty:
        raise ValueError("ZEIS: a geometria do Pilar não foi encontrada.")
    if not pilar.geometry.is_valid.all():
        pilar.geometry = pilar.geometry.make_valid()
    pilar.to_file(CUTS / "zeis_pilar.geojson", driver="GeoJSON")

    spatial = {
        "pracas": add_spatial_classification(point_layer(pracas, "longitude", "latitude"), pilar),
        "wifi": add_spatial_classification(point_layer(wifi, "LONGITUDE", "LATITUDE"), pilar),
        "urbanismo": add_spatial_classification(point_layer(urbanismo, "longitude", "latitude"), pilar),
    }
    for name, frame in spatial.items():
        cut = frame.loc[frame["recorte_territorial"] != "Fora do recorte"].copy()
        cut.to_file(CUTS / f"{name}_pilar_entorno.geojson", driver="GeoJSON")
        save_csv(cut, CUTS / f"{name}_pilar_entorno.csv")

    log_recife = logradouros.loc[logradouros["bairro_normalizado"] == "RECIFE"].copy()
    save_csv(log_recife, CUTS / "logradouros_bairro_recife.csv")

    # Indicadores calculados; uma linha por métrica, com fonte e fórmula.
    families = cad.drop_duplicates("cod_familiar")
    race = cad["raca_cor"]
    indicators = [
        ("pessoas_cadunico", len(cad), "pessoas", "CadÚnico Pilar", "contagem de linhas"),
        ("familias_cadunico", cad["cod_familiar"].nunique(), "famílias", "CadÚnico Pilar", "cod_familiar distintos"),
        ("populacao_negra_pct", round(float(race.isin(["Preta", "Parda"]).mean() * 100), 2), "%", "CadÚnico Pilar", "pretas+pardas / pessoas"),
        ("bolsa_familia_pct", round(float((families["bolsa_familia"] == "Sim").mean() * 100), 2), "%", "CadÚnico Pilar", "famílias beneficiárias / famílias"),
        ("renda_per_capita_media", round(float(cad["vlr_renda_media"].mean()), 2), "R$/mês", "CadÚnico Pilar", "média de vlr_renda_media"),
        ("renda_familiar_media", round(float(families["vlr_renda_total"].mean()), 2), "R$/mês", "CadÚnico Pilar", "média familiar de vlr_renda_total"),
        ("area_zeis_pilar", round(float(pilar["AREA_HA"].sum()), 4), "ha", "ZEIS Pilar", "soma de AREA_HA"),
        ("wifi_zeis", int((spatial["wifi"]["recorte_territorial"] == "ZEIS Pilar").sum()), "pontos", "ZEIS Pilar", "pontos dentro do polígono"),
        ("wifi_entorno_500m", int((spatial["wifi"]["recorte_territorial"] == f"Entorno até {PILAR_BUFFER_METERS} m").sum()), "pontos", "Entorno", "pontos no buffer, fora da ZEIS"),
        ("vias_com_deficit", int(log_recife["desc_indica_pavimentacao"].astype("string").str.contains("Não Pavimentada|Parcialmente", case=False, na=False).sum()), "vias", "Bairro do Recife", "não pavimentadas + parcialmente pavimentadas"),
    ]
    indicator_frame = pd.DataFrame(indicators, columns=["indicador", "valor", "unidade", "territorio", "formula"])
    indicator_frame["fonte"] = "Fontes_Summerjob"
    indicator_frame["gerado_em_utc"] = datetime.now(timezone.utc).isoformat()
    save_csv(indicator_frame, GOLD / "indicadores_territoriais.csv")

    catalog = []
    for name, filename in CSV_FILES.items():
        catalog.append({"base": name, "arquivo": filename, "formato": "CSV", "camada": "bruta",
                        "encoding": encodings[name], "registros": len(tables[name]), "colunas": len(tables[name].columns)})
    catalog.extend([
        {"base": "zeis", "arquivo": "zoneamento-plano-diretor-zeis.geojson", "formato": "GeoJSON", "camada": "bruta", "encoding": "UTF-8", "registros": len(zeis), "colunas": len(zeis.columns)},
        {"base": "cadunico_pilar", "arquivo": "cadunico_pilar.csv", "formato": "CSV", "camada": "recorte", "encoding": "UTF-8-SIG", "registros": len(cad), "colunas": len(cad.columns)},
    ])
    save_csv(pd.DataFrame(catalog), GOLD / "catalogo_bases.csv")
    save_csv(pd.DataFrame(quality), GOLD / "relatorio_qualidade.csv")
    summary = {
        "status": "concluido",
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(),
        "buffer_metros": PILAR_BUFFER_METERS,
        "pessoas_cadunico_pilar": len(cad),
        "familias_cadunico_pilar": int(cad["cod_familiar"].nunique()),
        "arquivos_tratados": len(treated),
        "bases_com_recorte_espacial": list(spatial),
    }
    (GOLD / "resumo_execucao.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build_pipeline()
