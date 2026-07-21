import sys
from pathlib import Path
import logging
from tqdm import tqdm
from config import DATA_DIR
from src.database import init_db, insert_chunks, get_stats, clear_local_storage
from src.parser import DatasetParser
from src.embedder import Embedder

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Ingest")

def run_ingestion(data_dir=DATA_DIR, batch_size=64):
    data_path = Path(data_dir)
    if not data_path.exists():
        logger.error(f"Diretório de dados não encontrado: {data_path}")
        sys.exit(1)
        
    logger.info("1. Limpando dados locais anteriores e inicializando estrutura...")
    clear_local_storage()
    init_db()
    
    logger.info("2. Carregando e inicializando o parser de datasets...")
    parser = DatasetParser(data_path)
    
    logger.info("3. Carregando modelo de embeddings...")
    embedder = Embedder()
    
    files = list(data_path.glob("*"))
    logger.info(f"Encontrados {len(files)} arquivos no diretório {data_path}.")
    
    for file_path in tqdm(files, desc="Processando arquivos"):
        if file_path.is_dir() or file_path.suffix.lower() not in ['.json', '.csv', '.geojson']:
            continue
            
        chunks = parser.parse_file(file_path)
        if not chunks:
            continue
            
        contents = [c["content"] for c in chunks]
        embeddings = embedder.embed_batch(contents, batch_size=batch_size)
        
        for c, emb in zip(chunks, embeddings):
            c["embedding"] = emb
            
        insert_chunks(chunks)
        
    stats = get_stats()
    logger.info("✅ Ingestão e salvamento concluídos com sucesso!")
    logger.info(f"Total de chunks armazenados: {stats['total_chunks']}")
    logger.info(f"Total de arquivos indexados: {stats['total_files']}")

if __name__ == "__main__":
    run_ingestion()
