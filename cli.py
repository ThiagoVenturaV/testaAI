import sys
import logging
from src.rag_engine import RAGEngine

logging.basicConfig(level=logging.ERROR)

def main():
    print("=" * 70)
    print(" 🏙️ SISTEMA RAG - BASE DE DADOS 'FONTES SUMMERJOB' (RECIFE) ")
    print(" Inferência: Groq (Modelo: qwen/qwen3.6-27b) | Banco: PostgreSQL pgvector")
    print("=" * 70)
    print("Digite sua pergunta abaixo (ou 'sair' para encerrar).\n")

    rag = RAGEngine()

    while True:
        try:
            query = input("\n🔍 Sua pergunta: ").strip()
            if not query:
                continue
            if query.lower() in ["sair", "exit", "quit"]:
                print("Encerrando o sistema. Até logo!")
                break

            print("\n⏳ Pesquisando na base vetorial, re-ranqueando e gerando resposta com Groq (Qwen)...\n")
            result = rag.answer_query(query)

            print("=" * 70)
            print("💡 RESPOSTA DO MODELO (Qwen via Groq):")
            print("=" * 70)
            print(result["answer"])

            print("\n" + "-" * 70)
            print("📚 FONTES E TRECHOS RECUPERADOS (APÓS RERANKING):")
            print("-" * 70)
            for i, chunk in enumerate(result["reranked_chunks"], 1):
                score = chunk.get("rerank_score", chunk.get("similarity", 0))
                print(f"[{i}] Arquivo: {chunk['file_name']} | Relevância Score: {score:.4f}")
                print(f"    Resumo/Linha inicial: {chunk['content'][:150].replace('\n', ' ')}...")
                print("-" * 50)

        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário.")
            break
        except Exception as e:
            print(f"\n❌ Erro durante a consulta: {e}")

if __name__ == "__main__":
    main()
