
from rag.vector_store import (
    index_knowledge_base,
    search_knowledge_base
)


if __name__ == "__main__":

    print("\nIndexing telecom knowledge base...")

    total = index_knowledge_base()

    print(f"Successfully indexed {total} documents.")

    print("\nSearching for VPN troubleshooting information...")

    query = "Employee cannot connect to company VPN"

    results = search_knowledge_base(query, top_k=3)

    print("\nRetrieved documents:")

    for result in results:
        print("\nTitle:", result["metadata"]["title"])
        print("Category:", result["metadata"]["category"])
        print("Content:", result["content"])
        print("Distance:", round(result["distance"], 4))
