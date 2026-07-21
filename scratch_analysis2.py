import pandas as pd
import geopandas as gpd
import json
from pathlib import Path

data_dir = Path(r"C:\Users\thiag\Downloads\Fontes Summerjob")

info = {}

# 1. Pontes
try:
    g_pontes = gpd.read_file(list(data_dir.glob("*pontes-do-recife.geojson"))[0])
    info["total_pontes"] = len(g_pontes)
    info["amostra_pontes"] = [str(row['nome']) for _, row in g_pontes.head(10).iterrows() if 'nome' in row and pd.notna(row['nome'])]
except Exception as e:
    info["err_pontes"] = str(e)

# 2. ZEIS (Zonas Especiais de Interesse Social)
try:
    g_zeis = gpd.read_file(list(data_dir.glob("*zoneamento-plano-diretor-zeis.geojson"))[0])
    info["total_zeis"] = len(g_zeis)
    cols = [c for c in g_zeis.columns if c != 'geometry']
    info["cols_zeis"] = cols
    if 'nome' in cols or 'NOME' in cols:
        col = 'nome' if 'nome' in cols else 'NOME'
        info["amostra_zeis"] = [str(x) for x in g_zeis[col].dropna().head(10).tolist()]
except Exception as e:
    info["err_zeis"] = str(e)

# 3. Urbanismo Tático
try:
    csv_ut = list(data_dir.glob("*urbanismo-tatico-.csv"))[0]
    df_ut = pd.read_csv(csv_ut, sep=None, engine='python', encoding='latin1')
    info["total_intervencoes_urbanismo_tatico"] = len(df_ut)
    info["cols_urbanismo_tatico"] = list(df_ut.columns)
    info["amostra_urbanismo_tatico"] = df_ut.head(5).to_dict(orient='records')
except Exception as e:
    info["err_ut"] = str(e)

# 4. Programa Tá Aprumado Praças
try:
    csv_taprumado = list(data_dir.glob("*programa-ta-aprumado-pracas.csv"))[0]
    df_taprumado = pd.read_csv(csv_taprumado, sep=None, engine='python', encoding='latin1')
    info["total_pracas_ta_aprumado"] = len(df_taprumado)
    info["cols_ta_aprumado"] = list(df_taprumado.columns)
except Exception as e:
    info["err_taprumado"] = str(e)

# 5. Malha Cicloviária detalhes
try:
    csv_ciclo = list(data_dir.glob("*detalhes-da-implantacao-da-malha-cicloviaria-do-recife.csv"))[0]
    df_c = pd.read_csv(csv_ciclo, sep=None, engine='python', encoding='latin1')
    info["tipologias_cicloviarias"] = df_c['tipologia'].value_counts().to_dict() if 'tipologia' in df_c.columns else {}
    info["top_rotas"] = df_c[['rota', 'extensao', 'inauguracao']].head(7).to_dict(orient='records')
except Exception as e:
    info["err_ciclo"] = str(e)

with open("analysis_output.json", "w", encoding="utf-8") as f:
    json.dump(info, f, indent=2, ensure_ascii=False)
print("Análise concluída e salva em analysis_output.json")
