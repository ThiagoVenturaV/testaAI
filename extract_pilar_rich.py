import pandas as pd
import geopandas as gpd
import json
from pathlib import Path

LOCAL_DATA = Path("./Fontes_Summerjob")
DATA = LOCAL_DATA if LOCAL_DATA.exists() else Path(r"C:\Users\thiag\Downloads\Fontes Summerjob")
out = {}

# --- ZEIS COMPLETAS ---
try:
    g_zeis = gpd.read_file(list(DATA.glob("*zoneamento-plano-diretor-zeis.geojson"))[0])
    df_z = pd.DataFrame(g_zeis.drop(columns=['geometry']))
    df_z['AREA_HA'] = pd.to_numeric(df_z['AREA_HA'], errors='coerce')
    out['total_zeis'] = len(df_z)
    out['area_media_zeis'] = float(df_z['AREA_HA'].mean())
    out['pilar_zeis'] = df_z[df_z['NMNOME'].str.lower().str.contains('pilar', na=False)][['NMNOME','AREA_HA','PROPOSTA','OBJECTID']].to_dict(orient='records')
    # Todas as ZEIS com área (para ranking)
    out['zeis_ranking'] = df_z[['NMNOME','AREA_HA']].dropna().sort_values('AREA_HA', ascending=False).head(20).to_dict(orient='records')
    # ZEIS por bairro (campo BAIRRO)
    bairro_col = 'BAIRRO' if 'BAIRRO' in df_z.columns else None
    if bairro_col:
        out['zeis_rpa1_sample'] = df_z[df_z[bairro_col].str.strip() == ''][['NMNOME','AREA_HA']].head(10).to_dict(orient='records')
except Exception as e:
    out['err_zeis'] = str(e)

# --- PRAÇAS COMPLETAS ---
try:
    df_p = pd.read_csv(list(DATA.glob("*parques-e-pracas.csv"))[0], sep=None, engine='python', encoding='latin1')
    out['total_pracas'] = len(df_p)
    out['pracas_cols'] = list(df_p.columns)
    out['area_col'] = 'area' if 'area' in df_p.columns else None
    if 'area' in df_p.columns:
        df_p['area'] = pd.to_numeric(df_p['area'], errors='coerce')
        out['area_total_pracas_m2'] = float(df_p['area'].sum())
        out['area_media_prac_m2'] = float(df_p['area'].mean())
        out['top_bairros_area'] = df_p.groupby('nome_bairro')['area'].sum().sort_values(ascending=False).head(10).to_dict()
    if 'nome_bairro' in df_p.columns:
        out['pracas_por_bairro'] = df_p['nome_bairro'].value_counts().head(20).to_dict()
        out['recife_antigo_pracas'] = df_p[df_p['nome_bairro'].str.lower().str.contains('recife', na=False)][['nome_equip_urbano','tipo_equip_urbano','area','perimetro','latitude','longitude']].to_dict(orient='records')
except Exception as e:
    out['err_pracas'] = str(e)

# --- CICLOVIAS ---
try:
    df_c = pd.read_csv(list(DATA.glob("*detalhes-da-implantacao-da-malha-cicloviaria-do-recife.csv"))[0], sep=None, engine='python', encoding='latin1')
    out['total_rotas_cicloviarias'] = len(df_c)
    out['tipologias_ciclo'] = df_c['tipologia'].value_counts().to_dict() if 'tipologia' in df_c.columns else {}
    out['rotas_bairro_recife'] = df_c[df_c['bairros'].str.lower().str.contains('recife', na=False)][['rota','tipologia','sentido','percurso','extensao','inauguracao']].to_dict(orient='records') if 'bairros' in df_c.columns else []
    out['ciclovias_todas'] = df_c[['rota','tipologia','extensao','inauguracao']].to_dict(orient='records')
except Exception as e:
    out['err_ciclo'] = str(e)

# --- WIFI ---
try:
    df_w = pd.read_csv(list(DATA.glob("*localidades-do-conecta-recife-wifi.csv"))[0], sep=None, engine='python', encoding='latin1')
    out['total_wifi'] = len(df_w)
    out['wifi_cols'] = list(df_w.columns)
    if 'bairro' in df_w.columns:
        out['wifi_por_bairro_top'] = df_w['bairro'].value_counts().head(20).to_dict()
        out['wifi_recife_antigo'] = df_w[df_w['bairro'].str.lower().str.contains('recife', na=False)].to_dict(orient='records')
    out['wifi_sample'] = df_w.head(3).to_dict(orient='records')
except Exception as e:
    out['err_wifi'] = str(e)

# --- URBANISMO TATICO ---
try:
    df_ut = pd.read_csv(list(DATA.glob("*urbanismo-tatico-.csv"))[0], sep=None, engine='python', encoding='latin1')
    out['total_ut'] = len(df_ut)
    if 'ano' in df_ut.columns:
        out['ut_por_ano'] = df_ut['ano'].value_counts().sort_index().to_dict()
    if 'tipo' in df_ut.columns:
        out['ut_por_tipo'] = df_ut['tipo'].value_counts().to_dict()
    if 'bairro' in df_ut.columns:
        out['ut_por_bairro'] = df_ut['bairro'].value_counts().head(15).to_dict()
    out['ut_recife_antigo'] = df_ut[df_ut['bairro'].str.lower().str.contains('recife|pilar|brum|apolo', na=False)].to_dict(orient='records') if 'bairro' in df_ut.columns else []
except Exception as e:
    out['err_ut'] = str(e)

# --- MICRORREGIAO ---
try:
    g_micro = gpd.read_file(list(DATA.glob("*microrregiao.geojson"))[0])
    df_micro = pd.DataFrame(g_micro.drop(columns=['geometry']))
    out['microregioes_cols'] = list(df_micro.columns)
    out['microregioes_sample'] = df_micro.head(5).to_dict(orient='records')
except Exception as e:
    out['err_micro'] = str(e)

# --- BAIRROS ---
try:
    df_b = pd.read_csv(list(DATA.glob("*bairros-e-rpas-do-recife.csv"))[0], sep=None, engine='python', encoding='latin1')
    out['bairros_por_rpa'] = df_b['rpa'].value_counts().sort_index().to_dict()
    out['bairros_rpa1'] = df_b[df_b['rpa'] == 1]['Bairro'].tolist()
except Exception as e:
    out['err_bairros'] = str(e)

# --- TRECHOS LOGRADOUROS CSV ---
try:
    df_log = pd.read_csv(list(DATA.glob("*trechos-de-logradouros-por-bairro.csv"))[0], sep=None, engine='python', encoding='latin1')
    out['total_logradouros'] = len(df_log)
    out['log_cols'] = list(df_log.columns)
    if 'nomeBairro' in df_log.columns:
        out['logradouros_recife_antigo'] = df_log[df_log['nomeBairro'].str.lower().str.contains('recife', na=False)].to_dict(orient='records')
        out['log_recife_count'] = len(out['logradouros_recife_antigo'])
    if 'cod_indica_pavimentacao' in df_log.columns and 'nomeBairro' in df_log.columns:
        recife_log = df_log[df_log['nomeBairro'].str.lower().str.contains('recife', na=False)]
        out['pavimentacao_recife'] = recife_log['desc_indica_pavimentacao'].value_counts().to_dict()
except Exception as e:
    out['err_log'] = str(e)

with open("pilar_rich_data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False, default=str)

print(f"Total ZEIS: {out.get('total_zeis')}")
print(f"ZEIS Pilar: {out.get('pilar_zeis')}")
print(f"Praças Recife Antigo: {len(out.get('recife_antigo_pracas', []))}")
print(f"WiFi Recife Antigo: {len(out.get('wifi_recife_antigo', []))}")
print(f"Ciclovias Recife: {len(out.get('rotas_bairro_recife', []))}")
print(f"Logradouros Recife: {out.get('log_recife_count')}")
print(f"Pavimentação Recife: {out.get('pavimentacao_recife')}")
print(f"UT Recife/Pilar: {out.get('ut_recife_antigo')}")
print(f"Bairros RPA1: {out.get('bairros_rpa1')}")
