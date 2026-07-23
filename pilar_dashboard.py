"""Dashboard territorial baseado exclusivamente nas saídas do pipeline_dados.py."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parent
CUTS = ROOT / "dados" / "03_recortes"
GOLD = ROOT / "dados" / "04_indicadores"

st.set_page_config(page_title="Pilar | Diagnóstico territorial", page_icon="🗺️", layout="wide")


@st.cache_data(show_spinner=False)
def load_data():
    required = [
        CUTS / "cadunico_pilar.csv",
        CUTS / "logradouros_bairro_recife.csv",
        CUTS / "wifi_pilar_entorno.csv",
        CUTS / "pracas_pilar_entorno.csv",
        CUTS / "urbanismo_pilar_entorno.csv",
        GOLD / "indicadores_territoriais.csv",
        GOLD / "relatorio_qualidade.csv",
    ]
    missing = [path for path in required if not path.exists() or path.stat().st_size == 0]
    if missing:
        try:
            import subprocess
            subprocess.run(["python", str(ROOT / "pipeline_dados.py")], check=True)
        except Exception:
            pass
            
    still_missing = [str(path.relative_to(ROOT)) for path in required if not path.exists() or path.stat().st_size == 0]
    if still_missing:
        raise FileNotFoundError("Execute `python pipeline_dados.py`. Arquivos ausentes: " + ", ".join(still_missing))
        
    return tuple(pd.read_csv(path, encoding="utf-8-sig", low_memory=False) for path in required)


try:
    cad, streets, wifi, squares, urbanism, indicators, quality = load_data()
except Exception as exc:
    st.error(str(exc))
    st.stop()


def format_brl(value):
    """Formata números monetários no padrão brasileiro."""
    if pd.isna(value):
        return "R$ —"
    formatted = f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"

st.title("Comunidade do Pilar — diagnóstico territorial")
st.caption("Indicadores calculados pelo pipeline; dados simulados do dashboard PRIME não são utilizados.")

with st.sidebar:
    st.header("Filtros do CadÚnico")

    def options(column):
        return sorted(cad[column].dropna().astype(str).unique().tolist())

    races = st.multiselect("Raça/cor", options("raca_cor"), default=options("raca_cor"))
    years = sorted(pd.to_numeric(cad["ano_atualizacao"], errors="coerce").dropna().astype(int).unique().tolist())
    selected_years = st.multiselect("Ano de atualização", years, default=years)
    sexes = st.multiselect("Sexo", options("sexo"), default=options("sexo"))
    ages = st.multiselect("Faixa etária", options("faixa_etaria"), default=options("faixa_etaria"))
    education = st.multiselect("Escolaridade", options("escolaridade"), default=options("escolaridade"))
    benefits = st.multiselect("Bolsa Família", options("bolsa_familia"), default=options("bolsa_familia"))
    disabilities = st.multiselect("Pessoa com deficiência", options("possui_deficiencia"), default=options("possui_deficiencia"))
    street_situation = st.multiselect("Situação de rua", options("situacao_rua"), default=options("situacao_rua"))
    income = pd.to_numeric(cad["vlr_renda_media"], errors="coerce")
    min_income, max_income = float(income.min() or 0), float(income.max() or 0)
    income_range = st.slider("Renda per capita (R$)", min_income, max_income, (min_income, max_income))

year_series = pd.to_numeric(cad["ano_atualizacao"], errors="coerce")
income_series = pd.to_numeric(cad["vlr_renda_media"], errors="coerce")
mask = (
    cad["raca_cor"].astype(str).isin(races)
    & year_series.isin(selected_years)
    & cad["sexo"].astype(str).isin(sexes)
    & cad["faixa_etaria"].astype(str).isin(ages)
    & cad["escolaridade"].astype(str).isin(education)
    & cad["bolsa_familia"].astype(str).isin(benefits)
    & cad["possui_deficiencia"].astype(str).isin(disabilities)
    & cad["situacao_rua"].astype(str).isin(street_situation)
    & income_series.between(*income_range)
)
filtered = cad.loc[mask].copy()

st.subheader("Perfil filtrado")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Pessoas", f"{len(filtered):,}".replace(",", "."))
c2.metric("Famílias", filtered["cod_familiar"].nunique())
black_pct = filtered["raca_cor"].isin(["Preta", "Parda"]).mean() * 100 if len(filtered) else 0
c3.metric("População negra", f"{black_pct:.1f}%")
families = filtered.drop_duplicates("cod_familiar")
benefit_pct = (families["bolsa_familia"] == "Sim").mean() * 100 if len(families) else 0
c4.metric("Famílias no Bolsa Família", f"{benefit_pct:.1f}%")

r1, r2 = st.columns(2)
per_capita_mean = pd.to_numeric(filtered["vlr_renda_media"], errors="coerce").mean()
family_income_mean = pd.to_numeric(families["vlr_renda_total"], errors="coerce").mean()
r1.metric("Renda per capita média", format_brl(per_capita_mean))
r2.metric("Renda familiar média", format_brl(family_income_mean))

if filtered.empty:
    st.warning("Nenhum registro atende à combinação atual de filtros.")
else:
    a, b = st.columns(2)
    race_counts = filtered["raca_cor"].value_counts().rename_axis("Raça/cor").reset_index(name="Pessoas")
    a.plotly_chart(px.bar(race_counts, x="Raça/cor", y="Pessoas", title="Distribuição por raça/cor"), width="stretch")
    year_counts = year_series.loc[filtered.index].value_counts().sort_index().rename_axis("Ano").reset_index(name="Pessoas")
    b.plotly_chart(px.line(year_counts, x="Ano", y="Pessoas", markers=True, title="Ano da última atualização cadastral"), width="stretch")

    c, d = st.columns(2)
    age_counts = filtered["faixa_etaria"].value_counts().rename_axis("Faixa etária").reset_index(name="Pessoas")
    c.plotly_chart(px.bar(age_counts, x="Pessoas", y="Faixa etária", orientation="h", title="Faixa etária"), width="stretch")
    edu_counts = filtered["escolaridade"].value_counts().rename_axis("Escolaridade").reset_index(name="Pessoas")
    d.plotly_chart(px.bar(edu_counts, x="Pessoas", y="Escolaridade", orientation="h", title="Escolaridade"), width="stretch")

st.divider()
st.subheader("Território: ZEIS Pilar e entorno de 500 metros")
t1, t2, t3, t4 = st.columns(4)
lookup = indicators.set_index("indicador")["valor"].to_dict()
t1.metric("Área da ZEIS", f"{float(lookup.get('area_zeis_pilar', 0)):.2f} ha")
t2.metric("Wi-Fi dentro da ZEIS", int(float(lookup.get("wifi_zeis", 0))))
t3.metric("Wi-Fi no entorno", int(float(lookup.get("wifi_entorno_500m", 0))))
t4.metric("Vias com déficit", int(float(lookup.get("vias_com_deficit", 0))))

layers = []
for frame, label, lat, lon in [
    (wifi, "Wi-Fi", "LATITUDE", "LONGITUDE"),
    (squares, "Praças e áreas verdes", "latitude", "longitude"),
    (urbanism, "Urbanismo tático", "latitude", "longitude"),
]:
    if lat in frame and lon in frame:
        part = frame.copy()
        part["tipo_equipamento"] = label
        part["lat"] = pd.to_numeric(part[lat], errors="coerce")
        part["lon"] = pd.to_numeric(part[lon], errors="coerce")
        layers.append(part[["lat", "lon", "tipo_equipamento", "recorte_territorial"]].dropna())
map_data = pd.concat(layers, ignore_index=True) if layers else pd.DataFrame()
if not map_data.empty:
    st.plotly_chart(
        px.scatter_map(map_data, lat="lat", lon="lon", color="tipo_equipamento",
                       hover_data=["recorte_territorial"], zoom=14, height=520,
                       title="Equipamentos classificados por interseção espacial"),
        width="stretch",
    )

street_counts = streets["desc_indica_pavimentacao"].value_counts().rename_axis("Situação").reset_index(name="Vias")
st.plotly_chart(px.bar(street_counts, x="Situação", y="Vias", title="Pavimentação no Bairro do Recife"), width="stretch")

tab1, tab2, tab3 = st.tabs(["Microdados filtrados", "Indicadores e fórmulas", "Qualidade das bases"])
with tab1:
    st.dataframe(filtered.reset_index(drop=True), width="stretch", height=520)
    st.download_button("Baixar recorte filtrado (CSV)", filtered.to_csv(index=False).encode("utf-8-sig"), "cadunico_pilar_filtrado.csv", "text/csv")
with tab2:
    st.dataframe(indicators, width="stretch")
with tab3:
    st.dataframe(quality, width="stretch")

st.caption("Fonte: bases locais em Fontes_Summerjob. Reexecute `python pipeline_dados.py` após atualizar qualquer arquivo bruto.")
