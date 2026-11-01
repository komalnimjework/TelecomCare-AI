from rag.vector_store import (
    index_knowledge_base,
    search_knowledge_base,
    collection
)

print("\n--- RAG DIAGNOSTIC TEST ---")

# Refresh documents using upsert (no duplicate IDs).
total = index_knowledge_base()

print(f"\nDocuments indexed: {total}")
print(f"Documents in ChromaDB: {collection.count()}")

queries = [
    "Employee cannot connect to company VPN",
    "My VPN is connected, but I cannot access internal company applications."
]

for query in queries:

    print("\n" + "=" * 60)
    print("QUERY:", query)
    print("=" * 60)

    results = search_knowledge_base(query, top_k=5)

    for rank, result in enumerate(results, start=1):

        print(f"\nRank: {rank}")
        print("Title:", result["metadata"]["title"])
        print("Category:", result["metadata"]["category"])
        print("Distance:", round(result["distance"], 4))
        print("Content:", result["content"])

print("\n--- DIAGNOSTIC COMPLETED ---")