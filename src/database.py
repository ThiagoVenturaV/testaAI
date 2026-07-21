import psycopg2
from psycopg2.extras import execute_values
import json
import logging
import math
import pickle
import numpy as np
from pathlib import Path
from config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, EMBEDDING_DIMENSION, BASE_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Database")

# Arquivo para persistência local caso PostgreSQL/Docker não esteja ativo
LOCAL_STORAGE_FILE = BASE_DIR / "vector_store.pkl"

IN_MEMORY_CHUNKS = []
IN_MEMORY_VECTORS = None

def load_local_storage():
    global IN_MEMORY_CHUNKS, IN_MEMORY_VECTORS
    if LOCAL_STORAGE_FILE.exists():
        try:
            with open(LOCAL_STORAGE_FILE, "rb") as f:
                data = pickle.load(f)
                IN_MEMORY_CHUNKS = data.get("chunks", [])
                vectors = data.get("vectors", [])
                if len(vectors) > 0:
                    IN_MEMORY_VECTORS = np.array(vectors, dtype=np.float32)
                else:
                    IN_MEMORY_VECTORS = None
            logger.info(f"Carregados {len(IN_MEMORY_CHUNKS)} chunks do arquivo de armazenamento local ({LOCAL_STORAGE_FILE.name}).")
        except Exception as e:
            logger.error(f"Erro ao carregar banco local {LOCAL_STORAGE_FILE}: {e}")

def save_local_storage():
    global IN_MEMORY_CHUNKS, IN_MEMORY_VECTORS
    try:
        vectors = [c['embedding'] for c in IN_MEMORY_CHUNKS]
        with open(LOCAL_STORAGE_FILE, "wb") as f:
            pickle.dump({
                "chunks": IN_MEMORY_CHUNKS,
                "vectors": vectors
            }, f)
        if len(vectors) > 0:
            IN_MEMORY_VECTORS = np.array(vectors, dtype=np.float32)
        logger.info(f"Salvos {len(IN_MEMORY_CHUNKS)} chunks no banco vetorial local ({LOCAL_STORAGE_FILE.name}).")
    except Exception as e:
        logger.error(f"Erro ao salvar banco local {LOCAL_STORAGE_FILE}: {e}")

# Tentar carregar banco local no início
load_local_storage()

def get_connection():
    try:
        return psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            dbname=POSTGRES_DB,
            connect_timeout=2
        )
    except Exception:
        return None

def init_db():
    conn = get_connection()
    if conn is None:
        logger.info("PostgreSQL não conectado. Usando banco vetorial local persistente (vector_store.pkl).")
        load_local_storage()
        return False
        
    try:
        cur = conn.cursor()
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id SERIAL PRIMARY KEY,
            file_name TEXT NOT NULL,
            data_type TEXT NOT NULL,
            dataset_title TEXT,
            chunk_index INT NOT NULL,
            content TEXT NOT NULL,
            metadata JSONB,
            embedding VECTOR({EMBEDDING_DIMENSION})
        );
        """
        cur.execute(create_table_query)
        index_query = """
        CREATE INDEX IF NOT EXISTS document_chunks_embedding_hnsw_idx 
        ON document_chunks 
        USING hnsw (embedding vector_cosine_ops);
        """
        cur.execute(index_query)
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Banco PostgreSQL + pgvector + HNSW inicializado.")
        return True
    except Exception as e:
        logger.warning(f"Erro no PostgreSQL: {e}. Usando modo de banco local.")
        load_local_storage()
        return False

def clear_local_storage():
    global IN_MEMORY_CHUNKS, IN_MEMORY_VECTORS
    IN_MEMORY_CHUNKS = []
    IN_MEMORY_VECTORS = None
    if LOCAL_STORAGE_FILE.exists():
        LOCAL_STORAGE_FILE.unlink()

def insert_chunks(chunks_data):
    if not chunks_data:
        return
        
    # Salvar no PostgreSQL se disponível
    conn = get_connection()
    if conn is not None:
        try:
            cur = conn.cursor()
            insert_query = """
            INSERT INTO document_chunks (file_name, data_type, dataset_title, chunk_index, content, metadata, embedding)
            VALUES %s
            """
            records = []
            for item in chunks_data:
                records.append((
                    item['file_name'],
                    item['data_type'],
                    item.get('dataset_title', ''),
                    item['chunk_index'],
                    item['content'],
                    json.dumps(item.get('metadata', {})),
                    str(item['embedding'])
                ))
            execute_values(cur, insert_query, records)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.warning(f"Falha ao inserir no PostgreSQL: {e}")

    # Salvar no armazenamento local persistente
    for item in chunks_data:
        IN_MEMORY_CHUNKS.append({
            'id': len(IN_MEMORY_CHUNKS) + 1,
            'file_name': item['file_name'],
            'data_type': item['data_type'],
            'dataset_title': item.get('dataset_title', ''),
            'chunk_index': item['chunk_index'],
            'content': item['content'],
            'metadata': item.get('metadata', {}),
            'embedding': item['embedding']
        })
    save_local_storage()

def search_vector_similarity(query_embedding, top_k=20, data_type_filter=None):
    global IN_MEMORY_CHUNKS, IN_MEMORY_VECTORS
    
    # 1. Tentar busca via PostgreSQL pgvector
    conn = get_connection()
    if conn is not None:
        try:
            cur = conn.cursor()
            vector_str = str(query_embedding)
            
            if data_type_filter:
                query = """
                SELECT id, file_name, data_type, dataset_title, chunk_index, content, metadata,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM document_chunks
                WHERE data_type = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """
                cur.execute(query, (vector_str, data_type_filter, vector_str, top_k))
            else:
                query = """
                SELECT id, file_name, data_type, dataset_title, chunk_index, content, metadata,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM document_chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """
                cur.execute(query, (vector_str, vector_str, top_k))
                
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            if rows:
                results = []
                for r in rows:
                    results.append({
                        'id': r[0],
                        'file_name': r[1],
                        'data_type': r[2],
                        'dataset_title': r[3],
                        'chunk_index': r[4],
                        'content': r[5],
                        'metadata': r[6],
                        'similarity': float(r[7])
                    })
                return results
        except Exception as e:
            logger.warning(f"Erro na busca pgvector: {e}")

    # 2. Fallback via NumPy matriz vetorizada local (ultrarrápido)
    if not IN_MEMORY_CHUNKS:
        load_local_storage()
        
    if not IN_MEMORY_CHUNKS:
        return []

    q_vec = np.array(query_embedding, dtype=np.float32)
    q_norm = np.linalg.norm(q_vec)
    if q_norm > 0:
        q_vec = q_vec / q_norm

    if IN_MEMORY_VECTORS is None or len(IN_MEMORY_VECTORS) != len(IN_MEMORY_CHUNKS):
        vectors = [c['embedding'] for c in IN_MEMORY_CHUNKS]
        IN_MEMORY_VECTORS = np.array(vectors, dtype=np.float32)

    # Produto escalar para similaridade de cosseno com vetores normalizados
    similarities = np.dot(IN_MEMORY_VECTORS, q_vec)

    results = []
    for idx, sim in enumerate(similarities):
        item = IN_MEMORY_CHUNKS[idx]
        if data_type_filter and item['data_type'] != data_type_filter:
            continue
        res = dict(item)
        res['similarity'] = float(sim)
        results.append(res)

    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results[:top_k]

def get_stats():
    conn = get_connection()
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*), COUNT(DISTINCT file_name) FROM document_chunks;")
            total_chunks, total_files = cur.fetchone()
            cur.close()
            conn.close()
            if total_chunks > 0:
                return {"total_chunks": total_chunks, "total_files": total_files}
        except Exception:
            pass
            
    if not IN_MEMORY_CHUNKS:
        load_local_storage()

    unique_files = len(set(c['file_name'] for c in IN_MEMORY_CHUNKS))
    return {"total_chunks": len(IN_MEMORY_CHUNKS), "total_files": unique_files}
