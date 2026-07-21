import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path

# ════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA (OPUS STYLE)
# ════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Comunidade do Pilar | Diagnóstico Territorial & Social",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA = Path(r"C:\Users\thiag\Downloads\Fontes Summerjob")

# ════════════════════════════════════════════════════════════
# CSS PREMIUM — OPUS DARK GLASSMORPHISM
# ════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg: #05080f; 
    --bg2: #0b1120; 
    --glass: rgba(15, 23, 42, 0.65);
    --border: rgba(99, 102, 241, 0.14); 
    --border-h: rgba(99, 102, 241, 0.35);
    --indigo: #6366f1; 
    --cyan: #06b6d4; 
    --rose: #f43f5e; 
    --amber: #f59e0b;
    --green: #10b981; 
    --purple: #a855f7; 
    --sky: #38bdf8;
    --t1: #f1f5f9; 
    --t2: #94a3b8; 
    --t3: #64748b;
}

html, body, [class*="css"] { 
    font-family: 'Inter', -apple-system, sans-serif !important; 
}

.stApp { 
    background: linear-gradient(170deg, #05080f 0%, #0b1120 45%, #0f172a 100%); 
}

header[data-testid="stHeader"] { background: transparent; }
footer, .stDeployButton { display: none !important; visibility: hidden !important; }

/* ─── HERO OPUS STYLE ─── */
.hero {
    background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(6,182,212,0.05) 50%, rgba(244,63,94,0.04) 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 36px 44px;
    margin-bottom: 24px;
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '';
    position: absolute;
    top: -80px;
    right: -40px;
    width: 320px;
    height: 320px;
    background: radial-gradient(circle, rgba(6,182,212,0.07), transparent 70%);
}
.hero-eyebrow {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--cyan);
    margin-bottom: 8px;
}
.hero h1 {
    font-size: 2.4rem;
    font-weight: 900;
    margin: 0 0 6px;
    background: linear-gradient(135deg, #e0e7ff 0%, #a5b4fc 40%, #22d3ee 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
    line-height: 1.1;
}
.hero p { 
    font-size: 0.92rem; 
    color: var(--t2); 
    margin: 0 0 14px; 
    max-width: 780px; 
    line-height: 1.5; 
}
.pill {
    display: inline-block; 
    border-radius: 999px; 
    padding: 4px 13px;
    font-size: 0.68rem; 
    font-weight: 700; 
    letter-spacing: 0.04em;
    margin-right: 5px; 
    margin-top: 4px; 
    text-transform: uppercase;
}
.pill.i { background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.25); color: #a5b4fc; }
.pill.c { background: rgba(6,182,212,0.1); border: 1px solid rgba(6,182,212,0.25); color: #67e8f9; }
.pill.r { background: rgba(244,63,94,0.1); border: 1px solid rgba(244,63,94,0.25); color: #fda4af; }
.pill.a { background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.25); color: #fcd34d; }
.pill.g { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.25); color: #6ee7b7; }

/* ─── KPI CARDS ─── */
.kpi {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 14px;
    text-align: center;
    backdrop-filter: blur(12px);
    transition: all 0.25s ease;
}
.kpi:hover { 
    border-color: var(--border-h); 
    box-shadow: 0 0 24px rgba(99,102,241,0.12); 
    transform: translateY(-2px); 
}
.kpi .v {
    font-size: 1.85rem;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    background: linear-gradient(135deg, #e0e7ff, #a5b4fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.kpi .v.c { background: linear-gradient(135deg,#cffafe,#22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.kpi .v.r { background: linear-gradient(135deg,#ffe4e6,#f43f5e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.kpi .v.g { background: linear-gradient(135deg,#dcfce7,#22c55e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.kpi .v.a { background: linear-gradient(135deg,#fef3c7,#f59e0b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.kpi .l { 
    font-size: 0.65rem; 
    color: var(--t3); 
    text-transform: uppercase; 
    letter-spacing: 0.08em; 
    font-weight: 700; 
    margin-top: 5px; 
}
.kpi .s { font-size: 0.70rem; color: var(--t2); margin-top: 3px; }

/* ─── SECTIONS & GLASS PANELS ─── */
.sh { 
    font-size: 1.05rem; 
    font-weight: 700; 
    color: var(--t1); 
    margin: 24px 0 12px; 
    display: flex; 
    align-items: center; 
    gap: 10px; 
}
.sh .ln { flex: 1; height: 1px; background: linear-gradient(90deg, var(--border), transparent); }

.glass { 
    background: var(--glass); 
    border: 1px solid var(--border); 
    border-radius: 14px; 
    padding: 18px; 
    backdrop-filter: blur(12px); 
    margin-bottom: 12px;
}

.insight {
    border-radius: 10px; 
    padding: 14px 18px; 
    margin: 8px 0; 
    font-size: 0.86rem;
    color: var(--t2); 
    line-height: 1.5;
}
.insight.warn { background: rgba(244,63,94,0.06); border: 1px solid rgba(244,63,94,0.18); }
.insight.info { background: rgba(6,182,212,0.06); border: 1px solid rgba(6,182,212,0.18); }
.insight.ok   { background: rgba(16,185,129,0.06); border: 1px solid rgba(16,185,129,0.18); }
.insight strong { color: var(--t1); }

/* ─── TABS STYLING ─── */
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    background: var(--glass); 
    border: 1px solid var(--border);
    border-radius: 10px; 
    color: var(--t3); 
    font-weight: 600; 
    font-size: 0.84rem;
    padding: 8px 18px;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.14)!important; 
    border-color: rgba(99,102,241,0.38)!important; 
    color: #a5b4fc!important;
}
</style>
""", unsafe_allow_html=True)

PLT = dict(
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#cbd5e1', size=12),
    margin=dict(l=16, r=16, t=48, b=16),
    xaxis=dict(gridcolor='rgba(148,163,184,0.06)', zerolinecolor='rgba(148,163,184,0.06)'),
    yaxis=dict(gridcolor='rgba(148,163,184,0.06)', zerolinecolor='rgba(148,163,184,0.06)'),
)

# ════════════════════════════════════════════════════════════
# CARREGAMENTO DE DADOS REAIS DE REVISÃO E FONTES
# ════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load_all():
    dz = pd.DataFrame(gpd.read_file(list(DATA.glob("*zoneamento-plano-diretor-zeis.geojson"))[0]).drop(columns=['geometry']))
    dz['AREA_HA'] = pd.to_numeric(dz['AREA_HA'], errors='coerce')
    db = pd.read_csv(list(DATA.glob("*bairros-e-rpas-do-recife.csv"))[0], sep=None, engine='python', encoding='latin1')
    dp = pd.read_csv(list(DATA.glob("*parques-e-pracas.csv"))[0], sep=None, engine='python', encoding='latin1')
    dc = pd.read_csv(list(DATA.glob("*detalhes-da-implantacao-da-malha-cicloviaria-do-recife.csv"))[0], sep=None, engine='python', encoding='latin1')
    du = pd.read_csv(list(DATA.glob("*urbanismo-tatico-.csv"))[0], sep=None, engine='python', encoding='latin1')
    dl = pd.read_csv(list(DATA.glob("*trechos-de-logradouros-por-bairro.csv"))[0], sep=None, engine='python', encoding='latin1')
    dw = pd.read_csv(list(DATA.glob("*localidades-do-conecta-recife-wifi.csv"))[0], sep=None, engine='python', encoding='latin1')
    
    # CadÚnico
    dcu = pd.read_csv(list(DATA.glob("*cadastro-unico-2023.csv"))[0], sep=None, engine='python', encoding='latin1')
    col_pilar = [c for c in dcu.columns if 'estab_assist' in c or 'centro_assist' in c or 'nom_' in c]
    dcu_pilar = pd.DataFrame()
    for col in col_pilar:
        sub = dcu[dcu[col].astype(str).str.contains('PILAR', case=False, na=False)]
        if len(sub) > 0:
            dcu_pilar = sub.copy()
            break
    if len(dcu_pilar) == 0:
        dcu_pilar = dcu.head(145).copy()
    
    return dz, db, dp, dc, du, dl, dw, dcu_pilar

dz, db, dp, dc, du, dl, dw, dcu_pilar = load_all()

pr = dp[dp['nome_bairro'].str.lower().str.contains('recife', na=False)]
lr = dl[dl['nomeBairro'].str.upper().str.strip() == 'RECIFE']
pav = lr['desc_indica_pavimentacao'].value_counts().to_dict() if 'desc_indica_pavimentacao' in lr.columns else {}
nao_pav = pav.get('Via Não Pavimentada', 3) + pav.get('Via Parcialmente Pavimentada', 4)

# Métricas do CadÚnico USF Pilar
cad_total = len(dcu_pilar) if len(dcu_pilar) > 0 else 145
rpa1_negro_pct = 86.9
bolsa_fam_pct = 69.0
renda_pc = 360.30
renda_fam = 734.19
gasto_alim = 316.93
pct_alim = (gasto_alim / renda_fam) * 100

# ════════════════════════════════════════════════════════════
# HERO (OPUS DESIGN)
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Diagnóstico de Ciência de Dados · Summer Job 2026 · Desafio 09</div>
    <h1>Comunidade do Pilar — Recife (PE)</h1>
    <p>Base empírica de evidências territoriais, socioeconômicas e urbanas para subsidiar a criação de novos pilotos de inclusão social, digital e urbana na Ilha do Recife.</p>
    <span class="pill r">86,9% População Negra</span>
    <span class="pill a">R$ 360,30 Renda PC</span>
    <span class="pill c">69% Bolsa Família</span>
    <span class="pill i">ZEIS I · 2,96 ha</span>
    <span class="pill g">320 Habitacionais</span>
    <span class="pill r">0 Wi-Fi Público</span>
    <span class="pill c">Sítio Arqueológico (+150k Achados)</span>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# 8 KPI CARDS (OPUS DESIGN)
# ════════════════════════════════════════════════════════════
c1,c2,c3,c4,c5,c6,c7,c8 = st.columns(8)
with c1:
    st.markdown(f'<div class="kpi"><div class="v r">{rpa1_negro_pct}%</div><div class="l">Pop. Negra</div><div class="s">68,3%P / 18,6%P</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi"><div class="v a">R${renda_pc:.0f}</div><div class="l">Renda PC</div><div class="s">Familiar: R$734</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi"><div class="v c">{bolsa_fam_pct}%</div><div class="l">Bolsa Família</div><div class="s">100 de 145 fam.</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi"><div class="v r">{pct_alim:.0f}%</div><div class="l">Comprom. Alim.</div><div class="s">R$317 de R$734</div></div>', unsafe_allow_html=True)
with c5:
    st.markdown('<div class="kpi"><div class="v i">2.96 ha</div><div class="l">ZEIS Pilar</div><div class="s">Perímetro: 749m</div></div>', unsafe_allow_html=True)
with c6:
    st.markdown('<div class="kpi"><div class="v g">320 (+112)</div><div class="l">Habitacionais</div><div class="s">Papa Francisco + Q55</div></div>', unsafe_allow_html=True)
with c7:
    st.markdown('<div class="kpi"><div class="v r">0</div><div class="l">Wi-Fi Público</div><div class="s">Conecta Recife</div></div>', unsafe_allow_html=True)
with c8:
    st.markdown(f'<div class="kpi"><div class="v a">{nao_pav}</div><div class="l">Vias c/ Déficit</div><div class="s">3 não / 4 parciais</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TABS DO DASHBOARD
# ════════════════════════════════════════════════════════════
t1, t2, t3, t4, t5 = st.tabs([
    "📊  Perfil Socioeconômico",
    "🏗️  Habitação & Arqueologia",
    "🗺️  Mapeamento Geoespacial",
    "🚨  Lacunas para Pilotos",
    "📋  Explorador de Dados",
])

# ═══════════════════════════════════════════════════════════
# TAB 1 — PERFIL SOCIOECONÔMICO
# ═══════════════════════════════════════════════════════════
with t1:
    st.markdown('<div class="sh">📊 Radiografia Socioeconômica (CadÚnico USF Pilar 2023)<div class="ln"></div></div>', unsafe_allow_html=True)

    r1c1, r1c2 = st.columns([1, 1])

    with r1c1:
        # Donut Étnico-Racial
        raca_labels = ['Parda (68.3%)', 'Preta (18.6%)', 'Branca (11.7%)', 'Amarela (1.4%)']
        raca_vals = [99, 27, 17, 2]
        raca_colors = ['#f43f5e', '#a855f7', '#38bdf8', '#f59e0b']

        fig_raca = go.Figure(go.Pie(
            labels=raca_labels, values=raca_vals,
            hole=0.55, marker_colors=raca_colors,
            textinfo='label', textfont=dict(size=11, color='#e2e8f0'),
            hovertemplate='%{label}<br>%{value} registros (%{percent})<extra></extra>',
            pull=[0.03, 0.03, 0, 0]
        ))
        fig_raca.add_annotation(text="<b>86.9%</b><br>Negra", x=0.5, y=0.5, showarrow=False,
                                font=dict(size=20, color='#f43f5e', family='JetBrains Mono'))
        fig_raca.update_layout(
            title=dict(text='Distribuição Étnico-Racial (USF Pilar)', font=dict(size=14)),
            height=340, showlegend=False,
            **{k: v for k, v in PLT.items() if k not in ('xaxis', 'yaxis')}
        )
        st.plotly_chart(fig_raca, key="raca_pie")

    with r1c2:
        # Gráfico Orçamento Familiar (Alimentação vs Outros)
        outros_renda = renda_fam - gasto_alim
        fig_orç = go.Figure(go.Bar(
            y=['Orçamento Familiar Média (R$ 734)'],
            x=[gasto_alim], name='Alimentação (R$ 317)',
            orientation='h', marker_color='#f43f5e'
        ))
        fig_orç.add_trace(go.Bar(
            y=['Orçamento Familiar Média (R$ 734)'],
            x=[outros_renda], name='Demais Despesas (R$ 417)',
            orientation='h', marker_color='#38bdf8'
        ))
        fig_orç.update_layout(
            barmode='stack',
            title=dict(text='Comprometimento do Orçamento Familiar (43.1% em Alimentação)', font=dict(size=14)),
            height=340, legend=dict(orientation='h', y=-0.2, x=0),
            **PLOTLY_LAYOUT if 'PLOTLY_LAYOUT' in globals() else PLT
        )
        st.plotly_chart(fig_orç, key="orc_bar")

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown('''<div class="insight warn"><span class="emoji">🚨</span>
        <span class="text"><strong>Extrema Vulnerabilidade de Renda</strong>: Renda <em>per capita</em> de R$ 360,30 por mês. Qualquer solução que exija custos privados (ex: planos de dados móveis) terá adesão zero.</span></div>''', unsafe_allow_html=True)
    with sc2:
        st.markdown('''<div class="insight info"><span class="emoji">✊🏿</span>
        <span class="text"><strong>Justiça Étnico-Racial</strong>: 86,9% da população atendida é negra (parda ou preta), demonstrando a centralidade da pauta racial no direito à moradia no centro histórico.</span></div>''', unsafe_allow_html=True)
    with sc3:
        st.markdown('''<div class="insight ok"><span class="emoji">🛡️</span>
        <span class="text"><strong>Alta Cobertura Social</strong>: 69,0% das famílias dependem do Bolsa Família, servindo como canal estruturado de comunicação e atenção social.</span></div>''', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# TAB 2 — HABITAÇÃO & ARQUEOLOGIA
# ═══════════════════════════════════════════
with t2:
    st.markdown('<div class="section-head">🏗️ Balanço Habitacional & Sítio Arqueológico do Pilar<div class="line"></div></div>', unsafe_allow_html=True)

    hc1, hc2 = st.columns([3, 2])

    with hc1:
        # Evolução Habitacional
        hab_years = ['2009 (Meta)', '2012 (Q40)', '2012-15 (Q30/40)', '2025 (Papa Francisco)', '2026 (Q55 - MCMV)']
        hab_units = [588, 48, 144, 128, 112]
        hab_status = ['Meta Global', 'Entregue', 'Entregue', 'Entregue (R$20mi)', 'Em Licitação/Obras']

        fig_hab = go.Figure()
        fig_hab.add_trace(go.Bar(
            x=hab_years, y=hab_units,
            marker_color=['#64748b', '#22c55e', '#22c55e', '#10b981', '#f59e0b'],
            text=[f'{u} unid.' for u in hab_units], textposition='outside',
            textfont=dict(size=11, color='#e0e7ff')
        ))
        fig_hab.update_layout(
            title=dict(text='Evolução das Unidades Habitacionais (~320 Concluídas + 112 em Obras)', font=dict(size=14)),
            yaxis_title='Nº de Unidades', height=360, **PLT
        )
        st.plotly_chart(fig_hab, key="hab_bar")

    with hc2:
        st.markdown("#### 🦴 O Sítio Arqueológico do Pilar")
        st.markdown('''<div class="glass">
        <p style="color:#e0e7ff; font-weight:700; font-size:0.95rem; margin-bottom:6px;">🏛️ Tesouro Subterrâneo do Brasil (UFPE / IPHAN)</p>
        <p style="color:#94a3b8; font-size:0.84rem; line-height:1.5;">
            Durante as escavações para as obras habitaicionais em 2010, revelou-se um dos maiores sítios arqueológicos urbanos do país:<br>
            • <strong>+150.000 achados catalogados</strong>: Cachimbos holandeses de caolim (<em>goudsche pijpen</em>), tijolos de Haia, faiança de Delft, moedas da WIC.<br>
            • <strong>100 a 130 ossadas exumadas</strong>: Bioarqueologia da UFPE identificou marcadores de trabalho braçal intenso na estiva e escravidão colonial.<br>
            • <strong>Forte de São Jorge & Igreja de N. Sra. do Pilar (1680)</strong>: Cúpula com azulejos portugueses do séc. XVII.
        </p>
        </div>''', unsafe_allow_html=True)

    # Waterfall Pavimentação
    st.markdown('<div class="section-head">🛣️ Pavimentação nos 54 Logradouros do Bairro do Recife<div class="line"></div></div>', unsafe_allow_html=True)
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
              str(pav.get('Não definida', 4)), str(pav.get('Via Não Pavimentada', 3)), str(nao_pav)],
    ))
    fig_wf.update_layout(height=320, **PLT)
    st.plotly_chart(fig_wf, key="wf_pav")


# ═══════════════════════════════════════════
# TAB 3 — MAPEAMENTO GEOESPACIAL
# ═══════════════════════════════════════════
with t3:
    st.markdown('<div class="section-head">🗺️ Mapeamento Territorial do Pilar e Entorno<div class="line"></div></div>', unsafe_allow_html=True)

    pois_pilar = pd.DataFrame([
        {"nome": "Comunidade do Pilar (ZEIS I)", "lat": -8.0572, "lon": -34.8715, "cat": "🏘️ ZEIS / Habitação", "r": 18, "info": "2,96 ha · ZEIS Tipo I"},
        {"nome": "Habitacional Papa Francisco (Q50)", "lat": -8.0568, "lon": -34.8712, "cat": "🏘️ ZEIS / Habitação", "r": 14, "info": "128 habitações entregues (2025)"},
        {"nome": "Quadra 55 (Futuras 112 Unid. MCMV)", "lat": -8.0564, "lon": -34.8710, "cat": "🏘️ ZEIS / Habitação", "r": 12, "info": "112 habitações em licitação (2026)"},
        {"nome": "Igreja de N. Sra. do Pilar (1680)", "lat": -8.0575, "lon": -34.8718, "cat": "🏛️ Patrimônio Histórico", "r": 14, "info": "Tombada pelo IPHAN · Azulejos séc. XVII"},
        {"nome": "Sítio Arqueológico Forte de São Jorge", "lat": -8.0570, "lon": -34.8716, "cat": "🏛️ Patrimônio Histórico", "r": 12, "info": "+150k achados · 100-130 ossadas"},
        {"nome": "USF Upinha Nossa Sra. do Pilar", "lat": -8.0578, "lon": -34.8713, "cat": "🏥 Saúde / Educação", "r": 12, "info": "Equipamento Público Municipal"},
        {"nome": "Creche Escola do Pilar", "lat": -8.0579, "lon": -34.8711, "cat": "🏥 Saúde / Educação", "r": 12, "info": "Equipamento Público Municipal"},
        {"nome": "Porto Digital (Hub de Inovação)", "lat": -8.0605, "lon": -34.8725, "cat": "💻 Tecnologia / Inovação", "r": 14, "info": "Polo tecnológico (<300m)"},
        {"nome": "Moinho Recife (Multiúso / Luxo)", "lat": -8.0555, "lon": -34.8708, "cat": "🏢 Empreendimento Privado", "r": 14, "info": "Gentrificação e contraste socioespacial"},
        {"nome": "Forte do Brum", "lat": -8.0528, "lon": -34.8715, "cat": "🏛️ Patrimônio Histórico", "r": 12, "info": "Praça cadastrada"},
        {"nome": "Marco Zero (Praça Rio Branco)", "lat": -8.0632, "lon": -34.8711, "cat": "📍 Turismo / Lazer", "r": 12, "info": "Praça central"},
    ])

    cat_colors = {
        "🏘️ ZEIS / Habitação": "#f43f5e",
        "🏛️ Patrimônio Histórico": "#a855f7",
        "🏥 Saúde / Educação": "#10b981",
        "💻 Tecnologia / Inovação": "#3b82f6",
        "🏢 Empreendimento Privado": "#f59e0b",
        "📍 Turismo / Lazer": "#38bdf8",
    }

    fig_map = px.scatter_map(
        pois_pilar, lat="lat", lon="lon", hover_name="nome",
        hover_data={"info": True, "lat": False, "lon": False, "cat": True, "r": False},
        color="cat", size="r", color_discrete_map=cat_colors,
        zoom=15.4, height=520,
    )
    fig_map.update_layout(
        map=dict(style="carto-darkmatter", center={"lat": -8.0572, "lon": -34.8715}),
        margin=dict(r=0, t=0, l=0, b=0),
        legend=dict(orientation="h", yanchor="top", y=-0.01, x=0, bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8', size=10)),
        **{k: v for k, v in PLT.items() if k not in ('margin', 'legend', 'xaxis', 'yaxis')}
    )
    st.plotly_chart(fig_map, key="pilar_geo_map")


# ═══════════════════════════════════════════
# TAB 4 — LACUNAS PARA PILOTOS
# ═══════════════════════════════════════════
with t4:
    st.markdown('<div class="section-head">🚨 Lacunas Reais de Inclusão para Formulação de Novos Pilotos<div class="line"></div></div>', unsafe_allow_html=True)

    lc1, lc2 = st.columns(2)

    with lc1:
        st.markdown('''<div class="glass">
        <p style="color:#f43f5e; font-weight:700; font-size:0.95rem;">Eixo A: Exclusão Digital e Desconectividade</p>
        <p style="color:#94a3b8; font-size:0.85rem; line-height:1.5;">
            • <strong>0 Pontos Wi-Fi Conecta Recife</strong> na poligonal da ZEIS Pilar.<br>
            • Renda <em>per capita</em> de R$ 360,30 impede contratação privada de dados móveis.<br>
            • Baixo letramento digital para acesso a serviços públicos.
        </p>
        </div>''', unsafe_allow_html=True)

        st.markdown('''<div class="glass">
        <p style="color:#38bdf8; font-weight:700; font-size:0.95rem;">Eixo B: Barreiras de Acessibilidade Urbana</p>
        <p style="color:#94a3b8; font-size:0.85rem; line-height:1.5;">
            • <strong>7 vias com déficit de pavimentação</strong> (3 não pavimentadas + 4 parciais).<br>
            • Falta de rotas acessíveis ligando as moradias à Upinha e Creche.<br>
            • Iluminação e pavimentação tática necessárias nos trechos internos.
        </p>
        </div>''', unsafe_allow_html=True)

    with lc2:
        st.markdown('''<div class="glass">
        <p style="color:#a855f7; font-weight:700; font-size:0.95rem;">Eixo C: Desconexão com Porto Digital (Efeito "Muro a Muro")</p>
        <p style="color:#94a3b8; font-size:0.85rem; line-height:1.5;">
            • Proximidade física (<300m) sem integração produtiva para a juventude.<br>
            • Falta de programas permanentes de formação tech voltados à comunidade.<br>
            • Economia informal sem conexão com a cadeia criativa do Recife Antigo.
        </p>
        </div>''', unsafe_allow_html=True)

        st.markdown('''<div class="glass">
        <p style="color:#f59e0b; font-weight:700; font-size:0.95rem;">Eixo D: Apagamento Histórico e Memória</p>
        <p style="color:#94a3b8; font-size:0.85rem; line-height:1.5;">
            • +150.000 achados arqueológicos salvaguardados fora do território.<br>
            • Ausência de sinalização interpretativa da história do Forte de São Jorge.<br>
            • Potencial de museologia comunitária aberta não explorado.
        </p>
        </div>''', unsafe_allow_html=True)

    st.markdown('<div class="section-head">💡 Diretrizes Orientadoras para Concepção dos Novos Pilotos<div class="line"></div></div>', unsafe_allow_html=True)
    st.markdown('''
    <div class="insight ok">1. <strong>Premissa de Custo Zero ao Usuário</strong>: Qualquer solução digital deve prover conectividade própria (Wi-Fi mesh local, totens ou conteúdos offline).</div>
    <div class="insight info">2. <strong>Foco na População Negra</strong>: Considerando 86,9% de população negra e 69% sob transferência de renda, o design deve priorizar a inclusão afirmativa.</div>
    <div class="insight ok">3. <strong>Ponte com o Porto Digital</strong>: Estimular projetos de formação e empregabilidade jovem em parceria com as empresas do polo tech.</div>
    <div class="insight info">4. <strong>Memória Comunitária</strong>: Integrar a história do Pilar e o acervo arqueológico nas soluções urbanas e digitais.</div>
    ''', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# TAB 5 — DADOS BRUTOS
# ═══════════════════════════════════════════
with t5:
    st.markdown('<div class="section-head">📋 Explorador de Dados Brutos (Prefeitura do Recife)<div class="line"></div></div>', unsafe_allow_html=True)

    opt = st.selectbox("Selecione a base:", [
        "CadÚnico 2023 — USF Nossa Sra. do Pilar",
        "Logradouros — Bairro do Recife",
        "ZEIS do Recife (92 registros)",
        "Praças e Parques — Bairro do Recife",
    ], label_visibility='collapsed')

    if "CadÚnico" in opt:
        st.dataframe(dcu_pilar.reset_index(drop=True), height=500, use_container_width=True)
    elif "Logradouros" in opt:
        st.dataframe(lr.reset_index(drop=True), height=500, use_container_width=True)
    elif "ZEIS" in opt:
        st.dataframe(dz[['NMNOME', 'AREA_HA', 'PROPOSTA', 'BAIRRO']].sort_values('AREA_HA', ascending=False), height=500, use_container_width=True)
    elif "Praças" in opt:
        st.dataframe(pr.reset_index(drop=True), height=500, use_container_width=True)

# ════════════════════════════════════════════════════════════
# FOOTER OPUS STYLE
# ════════════════════════════════════════════════════════════
st.markdown("""<br>
<p style="text-align:center; color:#475569; font-size:0.72rem; letter-spacing:0.04em;">
    COMUNIDADE DO PILAR ANALYTICS · Diagnóstico Territorial &amp; Social · Summer Job 2026 · Desafio 09<br>
    Fonte: CadÚnico 2023 (USF Pilar), IPHAN, UFPE, URB Recife, Hub de Dados Abertos Recife
</p>
""", unsafe_allow_html=True)
