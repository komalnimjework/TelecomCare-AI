from rag.vector_store import search_knowledge_base

query = (
    "My VPN is connected, but I cannot access "
    "internal company applications."
)

results = search_knowledge_base(query, top_k=3)

print("\n--- RETRIEVED SOURCES ---")

for index, result in enumerate(results, start=1):
    print(f"\nRank: {index}")
    print("Title:", result["metadata"]["title"])
    print("Category:", result["metadata"]["category"])
    print("Distance:", round(result["distance"], 4))
    print("Content:", result["content"])