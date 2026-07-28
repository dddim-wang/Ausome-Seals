from app.rag.service import create_rag_service


if __name__ == "__main__":
    service = create_rag_service()
    if service is None:
        raise SystemExit("No RAG knowledge directory was found")
    chunk_count = service.warm_up()
    print(f"RAG index ready: {chunk_count} chunks")
