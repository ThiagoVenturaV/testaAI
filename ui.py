import streamlit as st
import time
from src.rag_engine import RAGEngine
from src.database import get_stats

st.set_page_config(
    page_title="RAG Recife - Fontes Summerjob",
    page_icon="🏙️",
    layout="wide"
)

# Estilização CSS customizada
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 20px;
    }
    .stAlert {
        border-radius: 8px;
    }
    .metric-card {
        background-color: #F8FAFC;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_rag():
    return RAGEngine()

st.markdown('<p class="main-title">🏙️ Sistema RAG - Base de Dados "Fontes Summerjob" (Recife)</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Extrator de Informações Vetorial com Embedding, Reranking e Inferência Groq (Qwen 3.6-27B)</p>', unsafe_allow_html=True)

# Sidebar de Configurações e Estatísticas
with st.sidebar:
    st.image("https://img.icons8.com/color/96/city-buildings.png", width=70)
    st.header("⚙️ Painel de Controle")
    
    try:
        stats = get_stats()
        st.metric("Total de Chunks Indexados", stats["total_chunks"])
        st.metric("Total de Arquivos", stats["total_files"])
    except Exception:
        st.warning("PostgreSQL não conectado ou não ingerido ainda.")
        
    st.divider()
    st.subheader("Parâmetros do Pipeline")
    top_k_vec = st.slider("Top-K Busca Vetorial (1º Estágio)", 5, 50, 20)
    top_n_rerank = st.slider("Top-N Reranking (2º Estágio)", 1, 10, 5)
    filter_type = st.selectbox("Filtrar Tipo de Dado", ["Todos", "json_metadados", "csv_data", "geojson_data"])
    
    st.divider()
    st.info("💡 **Modelo de Inferência:** Qwen (Groq)\n**Banco Vetorial:** PostgreSQL + pgvector")

# Interface Principal de Busca
tab1, tab2 = st.tabs(["💬 Consulta & Extração RAG", "📁 Sobre a Base de Dados"])

with tab1:
    user_query = st.text_input("Digite sua pergunta sobre a base de dados do Recife:", placeholder="Ex: Quais são os parques e praças cadastrados em Recife e qual a área deles?")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        search_button = st.button("🔍 Extrair Informações", type="primary", use_container_width=True)
        
    if search_button and user_query.strip():
        with st.spinner("Buscando no pgvector, re-ranqueando trechos e consultando Groq Qwen..."):
            start_time = time.time()
            rag = load_rag()
            
            filter_val = None if filter_type == "Todos" else filter_type
            result = rag.answer_query(
                user_query,
                top_k_vector=top_k_vec,
                top_n_rerank=top_n_rerank,
                data_type_filter=filter_val
            )
            elapsed = time.time() - start_time
            
        st.success(f"Consulta finalizada em {elapsed:.2f} segundos!")
        
        st.subheader("💡 Resposta Sintetizada pelo Qwen (Groq):")
        st.markdown(result["answer"])
        
        st.divider()
        st.subheader("📚 Fontes e Chunks Re-ranqueados Utilizados (Top Rerank):")
        
        for idx, chunk in enumerate(result["reranked_chunks"], 1):
            score = chunk.get("rerank_score", chunk.get("similarity", 0.0))
            with st.expander(f"Trecho #{idx} - Arquivo: {chunk['file_name']} (Relevância: {score:.4f})"):
                st.write(f"**Tipo de Dado:** `{chunk['data_type']}` | **Dataset:** `{chunk.get('dataset_title', '')}`")
                st.code(chunk["content"], language="text")

with tab2:
    st.markdown("""
    ### 📂 Sobre o Dataset "Fontes Summerjob"
    Esta base de dados contém **65 arquivos públicos da Cidade do Recife**, abrangendo:
    - **Metadados e Dicionários de Dados JSON**: Descrições de esquemas de tabelas, campos, codificações e responsáveis.
    - **Tabelas CSV**: Informações sobre parques, praças, ciclovias, acessos ao Conecta Recife, censo SUAS e bairros.
    - **Geoprocessamento GeoJSON**: Feições de lotes, zoneamento do plano diretor, edificações, microrregiões e setores fiscais.
    """)
