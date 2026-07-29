"""Build the committed multilingual RAG vector cache."""

from app.rag.service import create_rag_service


def main() -> None:
    service = create_rag_service(build_missing=True)
    if service is None:
        raise SystemExit("RAG knowledge directory was not found")
    count = service.knowledge_base.build_embedding_index()
    print(f"Built multilingual embeddings for {count} knowledge chunks.")


if __name__ == "__main__":
    main()
