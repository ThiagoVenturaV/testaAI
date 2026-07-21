from sentence_transformers import SentenceTransformer
import logging
from config import EMBEDDING_MODEL_NAME

logger = logging.getLogger("Embedder")

class Embedder:
    def __init__(self, model_name=EMBEDDING_MODEL_NAME):
        logger.info(f"Carregando modelo de embedding: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
    def embed_text(self, text: str):
        """Gera embedding para um texto único (retorna lista de floats)."""
        vector = self.model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def embed_batch(self, texts: list[str], batch_size=32):
        """Gera embeddings em lote para performance elevada."""
        vectors = self.model.encode(texts, batch_size=batch_size, show_progress_bar=False, normalize_embeddings=True)
        return [v.tolist() for v in vectors]
