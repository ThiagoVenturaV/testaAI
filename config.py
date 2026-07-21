import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent

# Configurações do Banco de Dados PostgreSQL / pgvector
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "summerjob_db")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Diretório da Base de Dados de entrada
DATA_DIR = Path(os.getenv("DATA_DIR", r"C:\Users\thiag\Downloads\Fontes Summerjob"))

# Provedor LLM Groq & Modelo
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b")

# Modelo de Embedding
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 768))

# Reranker Model
RERANKER_MODEL_NAME = "ms-marco-MiniLM-L-6-v2"
