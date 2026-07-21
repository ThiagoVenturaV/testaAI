import logging
from src.database import search_vector_similarity
from src.embedder import Embedder
from src.reranker import Reranker
from src.llm_client import GroqLLMClient

logger = logging.getLogger("RAGEngine")

SYSTEM_PROMPT = """Você é um Assistente Especialista em Dados Abertos e Gestão Urbana da Cidade do Recife.
Sua missão é responder à dúvida do usuário utilizando ESTRITAMENTE as informações fornecidas no contexto dos trechos recuperados da base de dados "Fontes Summerjob" da Prefeitura do Recife.

Diretrizes:
1. Seja claro, preciso, objetivo e profissional.
2. Sempre cite os nomes dos arquivos fontes (ex: `resources_...geojson` ou `dicionario-...json`) de onde a informação foi extraída.
3. Se a informação não puder ser confirmada ou não estiver presente nos trechos do contexto, informe honestamente o que foi encontrado e o que faltou.
4. Ao citar valores, tabelas ou listas de atributos, formate-os de maneira legível usando Markdown.
"""

class RAGEngine:
    def __init__(self):
        logger.info("Inicializando componentes do RAGEngine...")
        self.embedder = Embedder()
        self.reranker = Reranker()
        self.llm_client = GroqLLMClient()

    def answer_query(self, query: str, top_k_vector: int = 25, top_n_rerank: int = 5, data_type_filter: str = None) -> dict:
        """
        Executa o pipeline RAG completo:
        1. Embedding da pergunta
        2. Busca por similaridade no PostgreSQL pgvector (Top-K)
        3. Re-ranqueamento em 2º estágio com Cross-Encoder (Top-N)
        4. Construção de prompt e síntese com Groq Qwen
        """
        # 1. Embedding da query
        query_vec = self.embedder.embed_text(query)
        
        # 2. Busca Vetorial
        vector_results = search_vector_similarity(query_vec, top_k=top_k_vector, data_type_filter=data_type_filter)
        
        if not vector_results:
            return {
                "query": query,
                "answer": "Nenhum documento relevante foi encontrado na base de dados.",
                "retrieved_chunks": [],
                "reranked_chunks": []
            }
            
        # 3. Reranking
        reranked_results = self.reranker.rerank(query, vector_results, top_n=top_n_rerank)
        
        # 4. Preparação do contexto para a LLM
        context_blocks = []
        for idx, chunk in enumerate(reranked_results, 1):
            block = (
                f"--- [TRECHO {idx}] ---\n"
                f"Arquivo Fonte: {chunk['file_name']}\n"
                f"Tipo de Dado: {chunk['data_type']}\n"
                f"Título do Dataset: {chunk.get('dataset_title', '')}\n"
                f"Conteúdo:\n{chunk['content']}\n"
            )
            context_blocks.append(block)
            
        full_context = "\n\n".join(context_blocks)
        
        user_prompt = (
            f"PERGUNTA DO USUÁRIO:\n{query}\n\n"
            f"CONTEXTO RECUPERADO DA BASE DE DADOS DO RECIFE:\n"
            f"{full_context}\n\n"
            f"Por favor, responda com base estritamente no contexto acima, citando os arquivos fontes."
        )
        
        # 5. Inferência Groq (Qwen 3.6-27B)
        llm_response = self.llm_client.generate_response(SYSTEM_PROMPT, user_prompt)
        
        return {
            "query": query,
            "answer": llm_response,
            "retrieved_chunks": vector_results,
            "reranked_chunks": reranked_results
        }
