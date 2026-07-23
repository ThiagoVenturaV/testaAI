import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path

# ════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════
st.set_page_config(page_title="PRIME Protocol | Sandbox Urbano — Ilha do Recife", page_icon="🔬", layout="wide", initial_sidebar_state="collapsed")

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "Fontes_Summerjob"
if not DATA.exists():
    DATA = Path(r"C:\Users\thiag\Downloads\Fontes Summerjob")

# ════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg: #05080f; --bg2: #0b1120; --glass: rgba(15,23,42,0.6);
    --border: rgba(99,102,241,0.12); --border-h: rgba(99,102,241,0.3);
    --indigo: #6366f1; --cyan: #06b6d4; --rose: #f43f5e; --amber: #f59e0b;
    --green: #10b981; --purple: #a855f7; --sky: #38bdf8;
    --t1: #f1f5f9; --t2: #94a3b8; --t3: #64748b;
}
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(170deg, #05080f 0%, #0b1120 45%, #0f172a 100%); }
header[data-testid="stHeader"] { background: transparent; }
footer, .stDeployButton { display: none !important; visibility: hidden !important; }

.hero {
    background: linear-gradient(135deg, rgba(99,102,241,0.06) 0%, rgba(6,182,212,0.04) 50%, rgba(244,63,94,0.03) 100%);
    border: 1px solid var(--border); border-radius: 20px;
    padding: 36px 44px; margin-bottom: 24px; backdrop-filter: blur(20px);
    position: relative; overflow: hidden;
}
.hero::after {
    content: ''; position: absolute; top: -80px; right: -40px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(6,182,212,0.06), transparent 70%);
}
.hero-eyebrow {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--cyan); margin-bottom: 8px;
}
.hero h1 {
    font-size: 2.4rem; font-weight: 900; margin: 0 0 6px;
    background: linear-gradient(135deg, #e0e7ff 0%, #a5b4fc 40%, #22d3ee 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em; line-height: 1.1;
}
.hero p { font-size: 0.92rem; color: var(--t2); margin: 0 0 14px; max-width: 700px; line-height: 1.5; }
.pill {
    display: inline-block; border-radius: 999px; padding: 4px 13px;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.04em;
    margin-right: 5px; margin-top: 4px; text-transform: uppercase;
}
.pill.i { background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.25); color: #a5b4fc; }
.pill.c { background: rgba(6,182,212,0.1); border: 1px solid rgba(6,182,212,0.25); color: #67e8f9; }
.pill.r { background: rgba(244,63,94,0.1); border: 1px solid rgba(244,63,94,0.25); color: #fda4af; }
.pill.a { background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.25); color: #fcd34d; }
.pill.g { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.25); color: #6ee7b7; }

.kpi {
    background: var(--glass); border: 1px solid var(--border);
    border-radius: 14px; padding: 18px 16px; text-align: center;
    backdrop-filter: blur(12px); transition: all 0.25s;
}
.kpi:hover { border-color: var(--border-h); box-shadow: 0 0 24px rgba(99,102,241,0.1); transform: translateY(-2px); }
.kpi .v {
    font-size: 1.9rem; font-weight: 800; font-family: 'JetBrains Mono', monospace;
    background: linear-gradient(135deg, #e0e7ff, #a5b4fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.kpi .v.c { background: linear-gradient(135deg,#cffafe,#22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.kpi .v.r { background: linear-gradient(135deg,#ffe4e6,#f43f5e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.kpi .v.g { background: linear-gradient(135deg,#dcfce7,#22c55e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.kpi .v.a { background: linear-gradient(135deg,#fef3c7,#f59e0b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.kpi .l { font-size: 0.66rem; color: var(--t3); text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; margin-top: 5px; }
.kpi .s { font-size: 0.72rem; color: var(--t2); margin-top: 3px; }

.sh { font-size: 1.05rem; font-weight: 700; color: var(--t1); margin: 24px 0 12px; display: flex; align-items: center; gap: 10px; }
.sh .ln { flex: 1; height: 1px; background: linear-gradient(90deg, var(--border), transparent); }

.glass { background: var(--glass); border: 1px solid var(--border); border-radius: 14px; padding: 18px; backdrop-filter: blur(12px); }

.pilot-card {
    background: var(--glass); border: 1px solid var(--border); border-radius: 14px;
    padding: 20px; backdrop-filter: blur(12px); margin-bottom: 10px; transition: all 0.25s;
}
.pilot-card:hover { border-color: var(--border-h); box-shadow: 0 0 20px rgba(99,102,241,0.08); }
.pilot-name { font-weight: 700; font-size: 0.95rem; color: var(--t1); margin-bottom: 4px; }
.pilot-hyp { font-size: 0.8rem; color: var(--t2); line-height: 1.4; margin-bottom: 8px; }
.status {
    display: inline-block; border-radius: 999px; padding: 2px 10px;
    font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
}
.status.active { background: rgba(16,185,129,0.15); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.3); }
.status.planned { background: rgba(99,102,241,0.15); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.3); }
.status.done { background: rgba(245,158,11,0.15); color: #fcd34d; border: 1px solid rgba(245,158,11,0.3); }

.insight {
    border-radius: 10px; padding: 14px 18px; margin: 8px 0; font-size: 0.85rem;
    color: var(--t2); line-height: 1.5;
}
.insight.warn { background: rgba(244,63,94,0.06); border: 1px solid rgba(244,63,94,0.15); }
.insight.info { background: rgba(6,182,212,0.06); border: 1px solid rgba(6,182,212,0.15); }
.insight.ok   { background: rgba(16,185,129,0.06); border: 1px solid rgba(16,185,129,0.15); }
.insight strong { color: var(--t1); }

.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    background: var(--glass); border: 1px solid var(--border);
    border-radius: 10px; color: var(--t3); font-weight: 600; font-size: 0.82rem;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.12)!important; border-color: rgba(99,102,241,0.35)!important; color: #a5b4fc!important;
}
</style>
""", unsafe_allow_html=True)

PLT = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#cbd5e1', size=12),
    margin=dict(l=16, r=16, t=48, b=16),
    xaxis=dict(gridcolor='rgba(148,163,184,0.06)', zerolinecolor='rgba(148,163,184,0.06)'),
    yaxis=dict(gridcolor='rgba(148,163,184,0.06)', zerolinecolor='rgba(148,163,184,0.06)'),
)

# ════════════════════════════════════════════
# DATA LOADING (REAL)
# ════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load():
    geojson_path = list(DATA.glob("*zoneamento-plano-diretor-zeis.geojson"))[0]
    try:
        dz = pd.DataFrame(gpd.read_file(geojson_path).drop(columns=['geometry']))
    except Exception:
        import json
        with open(geojson_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        dz = pd.DataFrame([feat.get('properties', {}) for feat in data.get('features', [])])
    dz['AREA_HA'] = pd.to_numeric(dz['AREA_HA'], errors='coerce')
    db = pd.read_csv(list(DATA.glob("*bairros-e-rpas-do-recife.csv"))[0], sep=None, engine='python', encoding='latin1')
    dp = pd.read_csv(list(DATA.glob("*parques-e-pracas.csv"))[0], sep=None, engine='python', encoding='latin1')
    dc = pd.read_csv(list(DATA.glob("*detalhes-da-implantacao-da-malha-cicloviaria-do-recife.csv"))[0], sep=None, engine='python', encoding='latin1')
    du = pd.read_csv(list(DATA.glob("*urbanismo-tatico-.csv"))[0], sep=None, engine='python', encoding='latin1')
    dl = pd.read_csv(list(DATA.glob("*trechos-de-logradouros-por-bairro.csv"))[0], sep=None, engine='python', encoding='latin1')
    dw = pd.read_csv(list(DATA.glob("*localidades-do-conecta-recife-wifi.csv"))[0], sep=None, engine='python', encoding='latin1')
    return dz, db, dp, dc, du, dl, dw

dz, db, dp, dc, du, dl, dw = load()
pr = dp[dp['nome_bairro'].str.lower().str.contains('recife', na=False)]
lr = dl[dl['nomeBairro'].str.upper().str.strip() == 'RECIFE']
pav = lr['desc_indica_pavimentacao'].value_counts().to_dict() if 'desc_indica_pavimentacao' in lr.columns else {}

# ════════════════════════════════════════════
# SIMULATED PILOT DATA
# ════════════════════════════════════════════
random.seed(42)
np.random.seed(42)

PILOTS = [
    {
        "id": "PLT-001", "nome": "Sinalização Sensorial Dinâmica",
        "desc": "QR Codes táteis com NFC nos pontos turísticos da Ilha para orientação em áudio de PcDs visuais e motoras.",
        "hipotese": "Placas com QR tátil + NFC reduzem em ≥40% o tempo de orientação de pessoas com deficiência visual nos pontos turísticos da Ilha.",
        "responsavel": "Equipe Alpha", "tipo": "🏙️ Urbana",
        "kpi_nome": "Redução de Tempo de Orientação", "kpi_meta": 40, "kpi_atual": 47.2, "kpi_un": "%",
        "status": "em_teste", "status_label": "active",
        "lat": -8.0528, "lon": -34.8715, "local": "Forte do Brum / Marco Zero",
        "eventos_total": 312, "usuarios_unicos": 89, "satisfacao": 4.3,
        "cor": "#6366f1",
    },
    {
        "id": "PLT-002", "nome": "Totem Digital Assistivo",
        "desc": "Ponto físico com assistente por voz e linguagem simples para navegar serviços da Ilha — público com baixa alfabetização digital.",
        "hipotese": "70% dos usuários com baixa alfabetização digital conseguem completar a jornada de busca de serviço no totem sem auxílio humano.",
        "responsavel": "Equipe Beta", "tipo": "💻 Digital",
        "kpi_nome": "Taxa de Conclusão Autônoma", "kpi_meta": 70, "kpi_atual": 63.5, "kpi_un": "%",
        "status": "em_teste", "status_label": "active",
        "lat": -8.0587, "lon": -34.8721, "local": "Praça Tiradentes",
        "eventos_total": 187, "usuarios_unicos": 54, "satisfacao": 3.8,
        "cor": "#06b6d4",
    },
    {
        "id": "PLT-003", "nome": "Passaporte de Experiências Inclusivas",
        "desc": "Rota gamificada acessível com check-ins presenciais para idosos e neurodivergentes — coleta de selos e recompensas locais.",
        "hipotese": "A rota gamificada gera ≥60% de taxa de conclusão (todos os pontos visitados) entre participantes 60+.",
        "responsavel": "Equipe Gamma", "tipo": "🤝 Social",
        "kpi_nome": "Taxa de Conclusão da Rota", "kpi_meta": 60, "kpi_atual": 72.1, "kpi_un": "%",
        "status": "em_teste", "status_label": "active",
        "lat": -8.0605, "lon": -34.8725, "local": "Rota: Brum → Marco Zero → Apolo",
        "eventos_total": 243, "usuarios_unicos": 67, "satisfacao": 4.6,
        "cor": "#f43f5e",
    },
]

def gen_events(pilot, n=50):
    tipos = ['conclusao', 'uso', 'feedback', 'abandono']
    cats = ['Acessibilidade Física', 'Usabilidade Digital', 'Satisfação Geral', 'Sugestão de Melhoria', 'Barreira Identificada']
    base = datetime(2026, 7, 21)
    rows = []
    for i in range(n):
        t = random.choice(tipos)
        rows.append({
            'piloto_id': pilot['id'], 'piloto_nome': pilot['nome'],
            'tipo': t,
            'categoria_ia': random.choice(cats),
            'metrica': round(random.uniform(0.5, 5.0), 1) if t != 'abandono' else 0,
            'hora': base - timedelta(hours=random.randint(0, 168), minutes=random.randint(0, 59)),
            'lat': pilot['lat'] + random.uniform(-0.002, 0.002),
            'lon': pilot['lon'] + random.uniform(-0.002, 0.002),
        })
    return pd.DataFrame(rows)

df_events = pd.concat([gen_events(p, n=p['eventos_total']//3) for p in PILOTS], ignore_index=True)
df_events = df_events.sort_values('hora', ascending=False).reset_index(drop=True)

# ════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">CESAR Summer Job 2026 · Desafio 09 · Cidade PRIME</div>
    <h1>Protocolo PRIME</h1>
    <p>Infraestrutura de experimentação e observabilidade para pilotos de inclusão social, digital e urbana na Ilha do Recife. Dados territoriais reais + pilotos instrumentados em tempo real.</p>
    <span class="pill i">Inclusive</span>
    <span class="pill c">Experimental</span>
    <span class="pill a">Monitorable</span>
    <span class="pill g">Sandbox Urbano</span>
    <span class="pill r">Ilha do Recife</span>
    <span class="pill i">ZEIS Pilar</span>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════
# KPI ROW
# ════════════════════════════════════════════
c1,c2,c3,c4,c5,c6,c7,c8 = st.columns(8)
with c1:
    st.markdown('<div class="kpi"><div class="v">3</div><div class="l">Pilotos Ativos</div><div class="s">Ilha do Recife</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi"><div class="v c">{sum(p["eventos_total"] for p in PILOTS)}</div><div class="l">Eventos Capturados</div><div class="s">Últimos 7 dias</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi"><div class="v g">{sum(p["usuarios_unicos"] for p in PILOTS)}</div><div class="l">Usuários Únicos</div><div class="s">Impactados</div></div>', unsafe_allow_html=True)
with c4:
    avg_sat = np.mean([p['satisfacao'] for p in PILOTS])
    st.markdown(f'<div class="kpi"><div class="v a">{avg_sat:.1f}/5</div><div class="l">Satisfação Média</div><div class="s">Todos os pilotos</div></div>', unsafe_allow_html=True)
with c5:
    st.markdown('<div class="kpi"><div class="v r">2.96 ha</div><div class="l">ZEIS Pilar</div><div class="s">Hab. Social</div></div>', unsafe_allow_html=True)
with c6:
    st.markdown(f'<div class="kpi"><div class="v">{len(pr)}</div><div class="l">Praças no Bairro</div><div class="s">Pontos de teste</div></div>', unsafe_allow_html=True)
with c7:
    nao_pav = pav.get('Via Não Pavimentada', 3) + pav.get('Via Parcialmente Pavimentada', 4)
    st.markdown(f'<div class="kpi"><div class="v r">{nao_pav}</div><div class="l">Vias com Déficit</div><div class="s">Barreira urbana</div></div>', unsafe_allow_html=True)
with c8:
    st.markdown('<div class="kpi"><div class="v r">0</div><div class="l">Wi-Fi no Pilar</div><div class="s">Exclusão digital</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════
t1, t2, t3, t4 = st.tabs([
    "🔬  Painel de Pilotos",
    "📡  Observabilidade em Tempo Real",
    "🗺️  Diagnóstico Territorial",
    "📊  Análise Comparativa",
])

# ═══════════════════════════════════════════
# TAB 1 — PAINEL DE PILOTOS
# ═══════════════════════════════════════════
with t1:
    st.markdown('<div class="sh">🔬 Pilotos Ativos na Ilha do Recife<div class="ln"></div></div>', unsafe_allow_html=True)

    for p in PILOTS:
        col_info, col_gauge, col_funnel = st.columns([2, 1, 1])

        with col_info:
            hit = "✅" if p['kpi_atual'] >= p['kpi_meta'] else "⏳"
            st.markdown(f'''<div class="pilot-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div class="pilot-name">{p["tipo"]} {p["nome"]}</div>
                    <span class="status {p['status_label']}">{p['status']}</span>
                </div>
                <div class="pilot-hyp">📐 <strong>Hipótese:</strong> {p["hipotese"]}</div>
                <div style="display:flex; gap:24px; font-size:0.8rem; color:var(--t2);">
                    <span>📍 {p["local"]}</span>
                    <span>👤 {p["responsavel"]}</span>
                    <span>📊 {p["eventos_total"]} eventos</span>
                    <span>👥 {p["usuarios_unicos"]} únicos</span>
                    <span>⭐ {p["satisfacao"]}/5</span>
                </div>
            </div>''', unsafe_allow_html=True)

        with col_gauge:
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=p['kpi_atual'], number={'suffix': p['kpi_un'], 'font': dict(size=32, family='JetBrains Mono', color='#e0e7ff')},
                delta={'reference': p['kpi_meta'], 'valueformat': '.1f', 'suffix': p['kpi_un'],
                       'increasing': {'color': '#22c55e'}, 'decreasing': {'color': '#f43f5e'}},
                title={'text': p['kpi_nome'], 'font': dict(size=10, color='#94a3b8')},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': '#475569'},
                    'bar': {'color': p['cor'], 'thickness': 0.25},
                    'bgcolor': 'rgba(0,0,0,0)', 'bordercolor': 'rgba(99,102,241,0.15)',
                    'steps': [{'range': [0, p['kpi_meta']], 'color': 'rgba(99,102,241,0.05)'}],
                    'threshold': {'line': {'color': '#22d3ee', 'width': 2}, 'thickness': 0.8, 'value': p['kpi_meta']}
                }
            ))
            fig_g.update_layout(height=180, **PLT)
            st.plotly_chart(fig_g, key=f"gauge_{p['id']}")

        with col_funnel:
            ev = df_events[df_events['piloto_id'] == p['id']]
            tc = ev['tipo'].value_counts()
            fig_f = go.Figure(go.Funnel(
                y=['Uso', 'Conclusão', 'Feedback', 'Abandono'],
                x=[tc.get('uso', 0), tc.get('conclusao', 0), tc.get('feedback', 0), tc.get('abandono', 0)],
                textinfo="value+percent initial",
                marker_color=[p['cor'], '#22c55e', '#f59e0b', '#f43f5e'],
                connector_line_color='rgba(99,102,241,0.15)',
                textfont=dict(size=10, color='#e0e7ff'),
            ))
            fig_f.update_layout(height=180, showlegend=False, **PLT)
            st.plotly_chart(fig_f, key=f"funnel_{p['id']}")

    # Map dos pilotos
    st.markdown('<div class="sh">🗺️ Localização dos Pilotos na Ilha<div class="ln"></div></div>', unsafe_allow_html=True)
    pilot_df = pd.DataFrame(PILOTS)
    fig_pm = px.scatter_map(
        pilot_df, lat='lat', lon='lon', hover_name='nome',
        hover_data={'tipo': True, 'status': True, 'eventos_total': True, 'lat': False, 'lon': False, 'cor': False,
                    'id': False, 'desc': False, 'hipotese': False, 'responsavel': False, 'kpi_nome': False,
                    'kpi_meta': False, 'kpi_atual': False, 'kpi_un': False, 'status_label': False,
                    'local': False, 'usuarios_unicos': False, 'satisfacao': False},
        color='tipo',
        color_discrete_map={'🏙️ Urbana': '#6366f1', '💻 Digital': '#06b6d4', '🤝 Social': '#f43f5e'},
        size=[20]*len(pilot_df), zoom=15, height=400,
    )
    # Adicionar praças como segunda camada
    pracas_pts = pr[['nome_equip_urbano', 'latitude', 'longitude']].dropna()
    fig_pm.add_trace(go.Scattermap(
        lat=pracas_pts['latitude'], lon=pracas_pts['longitude'],
        mode='markers', marker=dict(size=7, color='rgba(168,85,247,0.5)'),
        name='Praças/Áreas Verdes', text=pracas_pts['nome_equip_urbano'],
        hovertemplate='%{text}<extra>Praça</extra>'
    ))
    fig_pm.update_layout(
        map=dict(style="carto-darkmatter", center={"lat": -8.057, "lon": -34.871}),
        margin=dict(r=0, t=0, l=0, b=0),
        legend=dict(orientation='h', y=-0.02, x=0, bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8', size=10)),
        **{k: v for k, v in PLT.items() if k not in ('margin', 'legend', 'xaxis', 'yaxis')}
    )
    st.plotly_chart(fig_pm, key="pilot_map")


# ═══════════════════════════════════════════
# TAB 2 — OBSERVABILIDADE
# ═══════════════════════════════════════════
with t2:
    st.markdown('<div class="sh">📡 Feed de Eventos (Simulação)<div class="ln"></div></div>', unsafe_allow_html=True)

    oc1, oc2 = st.columns([2, 1])

    with oc1:
        # Timeline de eventos por hora
        df_hour = df_events.copy()
        df_hour['dia'] = df_hour['hora'].dt.date.astype(str)
        df_hour['h'] = df_hour['hora'].dt.hour
        heat = df_hour.groupby(['dia', 'h']).size().reset_index(name='eventos')
        heat_pivot = heat.pivot(index='h', columns='dia', values='eventos').fillna(0)

        fig_heat = px.imshow(
            heat_pivot, aspect='auto',
            color_continuous_scale=[[0, '#0f172a'], [0.3, '#312e81'], [0.6, '#4338ca'], [1, '#22d3ee']],
            labels=dict(x='Dia', y='Hora', color='Eventos'),
            title='Heatmap Temporal — Volume de Eventos por Hora e Dia',
        )
        fig_heat.update_layout(height=320, coloraxis_showscale=True, **{k: v for k, v in PLT.items() if k not in ('xaxis', 'yaxis')})
        st.plotly_chart(fig_heat, key="heatmap")

    with oc2:
        # Classificação IA
        cat_counts = df_events['categoria_ia'].value_counts().reset_index()
        cat_counts.columns = ['Categoria', 'Eventos']
        fig_cat = px.bar(
            cat_counts, x='Eventos', y='Categoria', orientation='h',
            color='Eventos', color_continuous_scale=[[0, '#1e1b4b'], [1, '#6366f1']],
            title='Classificação Automática (IA)',
        )
        fig_cat.update_layout(height=320, coloraxis_showscale=False, yaxis=dict(categoryorder='total ascending'), **{k: v for k, v in PLT.items() if k != 'yaxis'})
        st.plotly_chart(fig_cat, key="ia_class")

    # Breakdown por tipo de evento
    st.markdown('<div class="sh">📊 Breakdown por Tipo de Evento × Piloto<div class="ln"></div></div>', unsafe_allow_html=True)

    oc3, oc4 = st.columns(2)
    with oc3:
        cross = df_events.groupby(['piloto_nome', 'tipo']).size().reset_index(name='count')
        fig_cross = px.bar(
            cross, x='count', y='piloto_nome', color='tipo', orientation='h',
            color_discrete_map={'uso': '#6366f1', 'conclusao': '#22c55e', 'feedback': '#f59e0b', 'abandono': '#f43f5e'},
            title='Eventos por Piloto e Tipo', barmode='stack',
        )
        fig_cross.update_layout(height=280, yaxis_title='', **{k: v for k, v in PLT.items() if k != 'yaxis'})
        st.plotly_chart(fig_cross, key="cross")

    with oc4:
        # Mapa de calor geoespacial
        fig_scatter = px.scatter_map(
            df_events, lat='lat', lon='lon', color='tipo',
            color_discrete_map={'uso': '#6366f1', 'conclusao': '#22c55e', 'feedback': '#f59e0b', 'abandono': '#f43f5e'},
            opacity=0.5, zoom=14.5, height=280,
            title='Dispersão Geoespacial dos Eventos',
        )
        fig_scatter.update_layout(
            map=dict(style="carto-darkmatter", center={"lat": -8.057, "lon": -34.871}),
            margin=dict(r=0, t=40, l=0, b=0),
            legend=dict(orientation='h', y=-0.05, x=0, bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8', size=9)),
            **{k: v for k, v in PLT.items() if k not in ('margin', 'legend', 'xaxis', 'yaxis')}
        )
        st.plotly_chart(fig_scatter, key="evt_scatter")

    # Últimos eventos (feed)
    st.markdown('<div class="sh">📋 Últimos Eventos Capturados<div class="ln"></div></div>', unsafe_allow_html=True)
    feed = df_events.head(12)[['hora', 'piloto_nome', 'tipo', 'categoria_ia', 'metrica']].copy()
    feed.columns = ['Timestamp', 'Piloto', 'Tipo', 'Categoria (IA)', 'Métrica']
    feed['Timestamp'] = feed['Timestamp'].dt.strftime('%d/%m %H:%M')
    st.dataframe(feed, use_container_width=True, height=340)


# ═══════════════════════════════════════════
# TAB 3 — DIAGNÓSTICO TERRITORIAL
# ═══════════════════════════════════════════
with t3:
    st.markdown('<div class="sh">🗺️ Diagnóstico de Lacunas — Ilha do Recife (Dados Reais)<div class="ln"></div></div>', unsafe_allow_html=True)

    st.markdown('''<div class="insight warn">⚠️ <strong>Zero pontos de Wi-Fi público (Conecta Recife)</strong> registrados dentro da poligonal da ZEIS Pilar. Dos 472 pontos do município, a comunidade está completamente excluída da cobertura de inclusão digital pública.</div>''', unsafe_allow_html=True)
    st.markdown(f'''<div class="insight warn">⚠️ <strong>{nao_pav} vias com déficit de pavimentação</strong> (3 não pavimentadas + 4 parcialmente) no Bairro do Recife — barreiras físicas de acessibilidade para PcDs e idosos.</div>''', unsafe_allow_html=True)
    st.markdown('''<div class="insight info">💡 A <strong>ZEIS Pilar (2,96 ha)</strong> possui apenas 9,6% da área média das 92 ZEIS do Recife (30,8 ha) — enclave habitacional de alta vulnerabilidade social no coração do ecossistema de inovação do Porto Digital.</div>''', unsafe_allow_html=True)

    dc1, dc2 = st.columns(2)

    with dc1:
        # Waterfall de lacunas
        fig_wf = go.Figure(go.Waterfall(
            orientation='v',
            x=['Vias Totais', 'Pavimentadas', 'Parc. Pavim.', 'Não Definida', 'Não Pavim.', 'Total Déficit'],
            y=[len(lr), -pav.get('Via Pavimentada', 43), -pav.get('Via Parcialmente Pavimentada', 4),
               -pav.get('Não definida', 4), -pav.get('Via Não Pavimentada', 3), 0],
            measure=['absolute', 'relative', 'relative', 'relative', 'relative', 'total'],
            connector_line_color='rgba(99,102,241,0.15)',
            increasing_marker_color='#22c55e', decreasing_marker_color='#f43f5e', totals_marker_color='#f59e0b',
            textposition='outside', textfont=dict(size=10, color='#94a3b8'),
            text=[str(len(lr)), str(pav.get('Via Pavimentada', 43)), str(pav.get('Via Parcialmente Pavimentada', 4)),
                  str(pav.get('Não definida', 4)), str(pav.get('Via Não Pavimentada', 3)),
                  str(nao_pav)],
        ))
        fig_wf.update_layout(title=dict(text='Waterfall — Pavimentação do Bairro do Recife', font=dict(size=13)), height=360, **PLT)
        st.plotly_chart(fig_wf, key="waterfall")

    with dc2:
        # ZEIS comparativo
        top_z = dz[['NMNOME', 'AREA_HA']].dropna().sort_values('AREA_HA', ascending=False)
        top_z = top_z[top_z['AREA_HA'] < 120].head(15).sort_values('AREA_HA')
        is_p = top_z['NMNOME'].str.lower().str.contains('pilar')

        fig_z = go.Figure(go.Bar(
            x=top_z['AREA_HA'], y=top_z['NMNOME'], orientation='h',
            marker_color=['#f43f5e' if p else 'rgba(99,102,241,0.45)' for p in is_p],
            text=[f'{v:.1f}' for v in top_z['AREA_HA']], textposition='outside',
            textfont=dict(size=9, color='#94a3b8'),
        ))
        fig_z.add_vline(x=dz['AREA_HA'].median(), line_dash="dash", line_color="#22d3ee", line_width=1,
                        annotation_text="Mediana", annotation_font_color="#22d3ee", annotation_font_size=10)
        fig_z.update_layout(title=dict(text='ZEIS por Área — Pilar em Destaque', font=dict(size=13)), height=360, showlegend=False, yaxis_title='', **PLT)
        st.plotly_chart(fig_z, key="zeis_bar")

    # Praças como pontos de teste
    st.markdown('<div class="sh">🌳 Pontos Públicos Disponíveis para Pilotos (Praças e Áreas Verdes)<div class="ln"></div></div>', unsafe_allow_html=True)
    eq = pr[['nome_equip_urbano', 'tipo_equip_urbano']].copy()
    eq.columns = ['Equipamento', 'Tipo']
    cols_eq = st.columns(4)
    for i, (_, row) in enumerate(eq.iterrows()):
        icon = "🌳" if "Verde" in str(row['Tipo']) else "🏛️"
        with cols_eq[i % 4]:
            st.markdown(f'<div class="glass" style="padding:10px 14px; margin-bottom:6px; font-size:0.82rem;"><span>{icon}</span> <strong style="color:#e0e7ff">{row["Equipamento"]}</strong><br><span style="color:#64748b; font-size:0.7rem;">{row["Tipo"]}</span></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# TAB 4 — ANÁLISE COMPARATIVA
# ═══════════════════════════════════════════
with t4:
    st.markdown('<div class="sh">📊 Comparação Multi-Piloto (Radar + Métricas)<div class="ln"></div></div>', unsafe_allow_html=True)

    ac1, ac2 = st.columns([3, 2])

    with ac1:
        cats = ['Alcance', 'Engajamento', 'Satisfação', 'Conclusão', 'Replicabilidade']
        fig_radar = go.Figure()
        for p in PILOTS:
            vals = [
                min(p['usuarios_unicos'] / 100 * 100, 100),
                min(p['eventos_total'] / 350 * 100, 100),
                p['satisfacao'] / 5 * 100,
                p['kpi_atual'],
                random.uniform(55, 90),
            ]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals + [vals[0]], theta=cats + [cats[0]],
                fill='toself', fillcolor=p['cor'].replace(')', ',0.08)').replace('rgb', 'rgba') if 'rgb' in p['cor'] else f"rgba({int(p['cor'][1:3],16)},{int(p['cor'][3:5],16)},{int(p['cor'][5:7],16)},0.08)",
                line=dict(color=p['cor'], width=2),
                name=p['nome'],
            ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(148,163,184,0.08)', tickfont=dict(size=9, color='#64748b')),
                angularaxis=dict(gridcolor='rgba(148,163,184,0.08)', tickfont=dict(size=11, color='#94a3b8')),
            ),
            title=dict(text='Radar de Desempenho Multidimensional', font=dict(size=14)),
            height=440, showlegend=True,
            legend=dict(orientation='h', y=-0.08, x=0, bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8', size=10)),
            **{k: v for k, v in PLT.items() if k not in ('xaxis', 'yaxis', 'legend')}
        )
        st.plotly_chart(fig_radar, key="radar")

    with ac2:
        st.markdown("#### 🏆 Score Geral por Piloto")
        for p in PILOTS:
            score = (p['kpi_atual'] / max(p['kpi_meta'], 1) * 40 + p['satisfacao'] / 5 * 30 + p['usuarios_unicos'] / 100 * 30)
            score = min(score, 100)
            bar_color = '#22c55e' if score >= 70 else '#f59e0b' if score >= 50 else '#f43f5e'
            st.markdown(f'''<div class="glass" style="margin-bottom:10px; padding:14px 18px;">
                <div style="font-weight:700; color:#e0e7ff; font-size:0.9rem; margin-bottom:6px;">{p["tipo"]} {p["nome"]}</div>
                <div style="background:rgba(15,23,42,0.8); border-radius:8px; height:24px; overflow:hidden; position:relative;">
                    <div style="background:{bar_color}; width:{score:.0f}%; height:100%; border-radius:8px; transition:width 0.5s;"></div>
                    <span style="position:absolute; top:3px; left:50%; transform:translateX(-50%); font-size:0.72rem; font-weight:700; color:#e0e7ff; font-family:'JetBrains Mono';">{score:.0f}/100</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:6px; font-size:0.72rem; color:#64748b;">
                    <span>KPI: {p['kpi_atual']}/{p['kpi_meta']}{p['kpi_un']}</span>
                    <span>⭐ {p['satisfacao']}/5</span>
                    <span>👥 {p['usuarios_unicos']}</span>
                </div>
            </div>''', unsafe_allow_html=True)

        st.markdown('''<div class="insight ok">✅ <strong>2 de 3 pilotos</strong> já superaram a meta de KPI definida na hipótese. O Totem Digital (63,5% vs. meta 70%) segue em evolução com feedback ativo.</div>''', unsafe_allow_html=True)

    # Evolução temporal dos eventos
    st.markdown('<div class="sh">📈 Evolução Temporal — Eventos Acumulados por Piloto<div class="ln"></div></div>', unsafe_allow_html=True)
    df_cum = df_events.copy()
    df_cum['dia'] = df_cum['hora'].dt.date
    daily = df_cum.groupby(['dia', 'piloto_nome']).size().reset_index(name='eventos')
    daily = daily.sort_values('dia')
    daily['acum'] = daily.groupby('piloto_nome')['eventos'].cumsum()

    fig_evo = px.line(
        daily, x='dia', y='acum', color='piloto_nome',
        color_discrete_map={p['nome']: p['cor'] for p in PILOTS},
        labels={'dia': 'Data', 'acum': 'Eventos Acumulados', 'piloto_nome': 'Piloto'},
    )
    fig_evo.update_traces(line_width=2.5)
    fig_evo.update_layout(
        height=320,
        legend=dict(orientation='h', y=-0.15, x=0, bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8', size=10)),
        **{k: v for k, v in PLT.items() if k != 'legend'}
    )
    st.plotly_chart(fig_evo, key="evo")

# ════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════
st.markdown("""<br>
<p style="text-align:center; color:#475569; font-size:0.7rem; letter-spacing:0.05em;">
    PROTOCOLO PRIME · Infraestrutura de Experimentação da Cidade PRIME · CESAR Summer Job 2026 · Desafio 09<br>
    Dados Territoriais: Hub de Dados Abertos — Prefeitura da Cidade do Recife · EMPREL · 65 bases processadas<br>
    Pilotos demonstrativos com dados simulados para prova de conceito
</p>
""", unsafe_allow_html=True)
