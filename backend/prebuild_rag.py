from app.rag.service import create_rag_service


if __name__ == "__main__":
    service = create_rag_service(build_missing=True)
    if service is None:
        raise SystemExit("No RAG knowledge directory was found")
    chunk_count = service.warm_up()
    print(f"RAG index ready: {chunk_count} chunks")
    if service.knowledge_base.embedding_index is not None:
        embedding_count = service.knowledge_base.build_embedding_index()
        print(f"Multilingual embedding index ready: {embedding_count} chunks")
