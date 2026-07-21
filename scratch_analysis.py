import pandas as pd
import geopandas as gpd
import json
from pathlib import Path

data_dir = Path(r"C:\Users\thiag\Downloads\Fontes Summerjob")

results = {}

# 1. Bairros e RPAs
try:
    csv_bairros = list(data_dir.glob("*bairros-e-rpas-do-recife.csv"))[0]
    df_bairros = pd.read_csv(csv_bairros, sep=None, engine='python', encoding='latin1')
    results["total_bairros"] = len(df_bairros)
    if 'rpa' in df_bairros.columns or 'RPA' in df_bairros.columns:
        col_rpa = 'rpa' if 'rpa' in df_bairros.columns else 'RPA'
        results["bairros_por_rpa"] = df_bairros[col_rpa].value_counts().to_dict()
    results["amostra_bairros"] = df_bairros.head(10).to_dict(orient='records')
except Exception as e:
    results["err_bairros"] = str(e)

# 2. Parques e Praças
try:
    csv_pracas = list(data_dir.glob("*parques-e-pracas.csv"))[0]
    df_pracas = pd.read_csv(csv_pracas, sep=None, engine='python', encoding='latin1')
    results["total_pracas_parques"] = len(df_pracas)
    if 'bairro' in df_pracas.columns:
        results["top_bairros_pracas"] = df_pracas['bairro'].value_counts().head(5).to_dict()
    results["cols_pracas"] = list(df_pracas.columns)
except Exception as e:
    results["err_pracas"] = str(e)

# 3. Malha Cicloviária
try:
    csv_ciclo = list(data_dir.glob("*detalhes-da-implantacao-da-malha-cicloviaria-do-recife.csv"))[0]
    df_ciclo = pd.read_csv(csv_ciclo, sep=None, engine='python', encoding='latin1')
    results["total_trechos_cicloviarios"] = len(df_ciclo)
    results["cols_cicloviarios"] = list(df_ciclo.columns)
    if 'extensao' in df_ciclo.columns or 'Extensão' in df_ciclo.columns:
        col_ext = 'extensao' if 'extensao' in df_ciclo.columns else 'Extensão'
        results["extensao_total_ciclo_km"] = float(df_ciclo[col_ext].astype(str).str.replace(',', '.').astype(float).sum())
except Exception as e:
    results["err_ciclo"] = str(e)

# 4. Conecta Recife WiFi
try:
    csv_wifi = list(data_dir.glob("*localidades-do-conecta-recife-wifi.csv"))[0]
    df_wifi = pd.read_csv(csv_wifi, sep=None, engine='python', encoding='latin1')
    results["total_pontos_wifi"] = len(df_wifi)
    if 'bairro' in df_wifi.columns or 'Bairro' in df_wifi.columns:
        col_b = 'bairro' if 'bairro' in df_wifi.columns else 'Bairro'
        results["top_bairros_wifi"] = df_wifi[col_b].value_counts().head(5).to_dict()
except Exception as e:
    results["err_wifi"] = str(e)

# 5. Prédios Públicos
try:
    geo_predios = list(data_dir.glob("*predios-publicos-da-prefeitura-do-recife.geojson"))[0]
    gdf_predios = gpd.read_file(geo_predios)
    results["total_predios_publicos"] = len(gdf_predios)
    results["cols_predios"] = [c for c in gdf_predios.columns if c != 'geometry']
except Exception as e:
    results["err_predios"] = str(e)

print(json.dumps(results, indent=2, ensure_ascii=False))
