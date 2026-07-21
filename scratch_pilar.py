import pandas as pd
import geopandas as gpd
import json
from pathlib import Path

data_dir = Path(r"C:\Users\thiag\Downloads\Fontes Summerjob")

pilar_data = {
    "zeis": [],
    "pracas_parques": [],
    "wifi": [],
    "urbanismo_tatico": [],
    "ciclovias": [],
    "logradouros": [],
    "predios_publicos": [],
    "patrimonio_historico": [],
    "bairro_recife_info": {}
}

# 1. ZEIS Pilar
try:
    g_zeis = gpd.read_file(list(data_dir.glob("*zoneamento-plano-diretor-zeis.geojson"))[0])
    for _, row in g_zeis.iterrows():
        row_str = str(row.to_dict()).lower()
        if "pilar" in row_str:
            pilar_data["zeis"].append({k: str(v) for k, v in row.items() if k != 'geometry' and pd.notna(v)})
except Exception as e:
    pilar_data["err_zeis"] = str(e)

# 2. Praças e Parques no Bairro do Recife / Pilar
try:
    csv_pracas = list(data_dir.glob("*parques-e-pracas.csv"))[0]
    df_pracas = pd.read_csv(csv_pracas, sep=None, engine='python', encoding='latin1')
    for _, row in df_pracas.iterrows():
        row_str = str(row.to_dict()).lower()
        if "pilar" in row_str or ("recife" in str(row.get("nome_bairro", "")).lower() and "bairro" in str(row.get("nome_bairro", "")).lower()):
            pilar_data["pracas_parques"].append({k: str(v) for k, v in row.items() if pd.notna(v)})
except Exception as e:
    pilar_data["err_pracas"] = str(e)

# 3. Wi-Fi Conecta Recife no Pilar / Bairro do Recife
try:
    csv_wifi = list(data_dir.glob("*localidades-do-conecta-recife-wifi.csv"))[0]
    df_wifi = pd.read_csv(csv_wifi, sep=None, engine='python', encoding='latin1')
    for _, row in df_wifi.iterrows():
        row_str = str(row.to_dict()).lower()
        if "pilar" in row_str or "recife" in str(row.get("bairro", "")).lower():
            pilar_data["wifi"].append({k: str(v) for k, v in row.items() if pd.notna(v)})
except Exception as e:
    pilar_data["err_wifi"] = str(e)

# 4. Urbanismo Tático no Pilar / Bairro do Recife
try:
    csv_ut = list(data_dir.glob("*urbanismo-tatico-.csv"))[0]
    df_ut = pd.read_csv(csv_ut, sep=None, engine='python', encoding='latin1')
    for _, row in df_ut.iterrows():
        row_str = str(row.to_dict()).lower()
        if "pilar" in row_str or "recife" in str(row.get("bairro", "")).lower() or "brum" in row_str:
            pilar_data["urbanismo_tatico"].append({k: str(v) for k, v in row.items() if pd.notna(v)})
except Exception as e:
    pilar_data["err_ut"] = str(e)

# 5. Ciclovias no Bairro do Recife / Pilar
try:
    csv_ciclo = list(data_dir.glob("*detalhes-da-implantacao-da-malha-cicloviaria-do-recife.csv"))[0]
    df_ciclo = pd.read_csv(csv_ciclo, sep=None, engine='python', encoding='latin1')
    for _, row in df_ciclo.iterrows():
        row_str = str(row.to_dict()).lower()
        if "pilar" in row_str or "recife" in str(row.get("bairros", "")).lower() or "brum" in row_str or "apolo" in row_str:
            pilar_data["ciclovias"].append({k: str(v) for k, v in row.items() if pd.notna(v)})
except Exception as e:
    pilar_data["err_ciclo"] = str(e)

# 6. Logradouros no Pilar / Bairro do Recife
try:
    csv_log = list(data_dir.glob("*trechos-de-logradouros-por-bairro.csv"))[0]
    df_log = pd.read_csv(csv_log, sep=None, engine='python', encoding='latin1')
    for _, row in df_log.iterrows():
        row_str = str(row.to_dict()).lower()
        if "pilar" in row_str:
            pilar_data["logradouros"].append({k: str(v) for k, v in row.items() if pd.notna(v)})
except Exception as e:
    pilar_data["err_log"] = str(e)

# 7. ZEPH (Zona Especial de Patrimônio Histórico-Cultural)
try:
    g_zeph = gpd.read_file(list(data_dir.glob("*zona-especial-de-patrimonio-historico-cultural.geojson"))[0])
    for _, row in g_zeph.iterrows():
        row_str = str(row.to_dict()).lower()
        if "pilar" in row_str or "recife" in row_str or "bairro do recife" in row_str:
            pilar_data["patrimonio_historico"].append({k: str(v) for k, v in row.items() if k != 'geometry' and pd.notna(v)})
except Exception as e:
    pilar_data["err_zeph"] = str(e)

with open("pilar_output.json", "w", encoding="utf-8") as f:
    json.dump(pilar_data, f, indent=2, ensure_ascii=False)

print("Análise da Comunidade do Pilar concluída com sucesso.")
