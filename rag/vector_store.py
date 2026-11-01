
import json
from pathlib import Path

import chromadb

from rag.embeddings import (
    generate_embeddings,
    generate_query_embedding
)

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_FILE = PROJECT_ROOT / "data" / "knowledge_base.json"

CHROMA_PATH = PROJECT_ROOT / "database" / "chroma_db"

# Persistent ChromaDB client
client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

# Create or reuse collection
collection = client.get_or_create_collection(
    name="telecom_knowledge",
    metadata={"hnsw:space": "cosine"}
)


def index_knowledge_base():
    """Load knowledge documents and store their embeddings."""

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        documents = json.load(file)

    ids = []
    texts = []
    metadatas = []

    for document in documents:
        ids.append(document["id"])

        texts.append(
            document["title"] + ". " + document["content"]
        )

        metadatas.append({
            "category": document["category"],
            "title": document["title"]
        })

    embeddings = generate_embeddings(texts)

    # Upsert prevents duplicate document IDs.
    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(ids)


def search_knowledge_base(query: str, top_k: int = 3):
    """Retrieve relevant troubleshooting documents."""

    query_embedding = generate_query_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count())
    )

    retrieved_documents = []

    if results["documents"]:
        for index, document in enumerate(results["documents"][0]):

            retrieved_documents.append({
                "content": document,
                "metadata": results["metadatas"][0][index],
                "distance": results["distances"][0][index]
            })

    return retrieved_documents
