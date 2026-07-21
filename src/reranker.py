import logging
try:
    from flashrank import Ranker, RerankRequest
    HAS_FLASHRANK = True
except ImportError:
    HAS_FLASHRANK = False

try:
    from sentence_transformers import CrossEncoder
    HAS_CROSS_ENCODER = True
except ImportError:
    HAS_CROSS_ENCODER = False

logger = logging.getLogger("Reranker")

class Reranker:
    def __init__(self, model_name="ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.ranker = None
        self.cross_encoder = None
        
        if HAS_FLASHRANK:
            try:
                logger.info("Inicializando Reranker via FlashRank...")
                self.ranker = Ranker(model_name="ms-marco-MiniLM-L-6-v2", cache_dir="/tmp/flashrank")
            except Exception as e:
                logger.warning(f"FlashRank falhou: {e}. Tentando CrossEncoder...")

        if self.ranker is None and HAS_CROSS_ENCODER:
            try:
                logger.info(f"Inicializando Reranker via SentenceTransformers CrossEncoder ({model_name})...")
                self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            except Exception as e:
                logger.warning(f"CrossEncoder não pôde ser carregado: {e}")

    def rerank(self, query: str, candidate_chunks: list[dict], top_n: int = 5) -> list[dict]:
        """
        Recebe a query e a lista de chunks recuperados no primeiro estágio (Vector DB).
        Retorna os Top-N chunks ordenados pela relevância do Reranker.
        """
        if not candidate_chunks:
            return []

        if self.ranker:
            try:
                passages = [
                    {"id": str(i), "text": c["content"], "meta": c}
                    for i, c in enumerate(candidate_chunks)
                ]
                rerank_req = RerankRequest(query=query, passages=passages)
                results = self.ranker.rerank(rerank_req)
                
                reranked = []
                for res in results[:top_n]:
                    meta = res["meta"]
                    meta["rerank_score"] = float(res.get("score", 0.0))
                    reranked.append(meta)
                return reranked
            except Exception as e:
                logger.warning(f"Erro durante rerank no FlashRank: {e}")

        if self.cross_encoder:
            try:
                pairs = [[query, c["content"]] for c in candidate_chunks]
                scores = self.cross_encoder.predict(pairs)
                for c, score in zip(candidate_chunks, scores):
                    c["rerank_score"] = float(score)
                sorted_chunks = sorted(candidate_chunks, key=lambda x: x["rerank_score"], reverse=True)
                return sorted_chunks[:top_n]
            except Exception as e:
                logger.warning(f"Erro durante rerank no CrossEncoder: {e}")

        # Fallback se nenhum reranker estiver pronto: retorna ordenado por similaridade de cosseno
        sorted_chunks = sorted(candidate_chunks, key=lambda x: x.get("similarity", 0), reverse=True)
        return sorted_chunks[:top_n]
