
from rag.answer_generator import generate_rag_answer


if __name__ == "__main__":

    question = "I cannot connect to my company VPN. What should I do?"

    print("\nEmployee Question:")
    print(question)

    print("\nGenerating RAG-based answer...\n")

    result = generate_rag_answer(question)

    print("Status:", result["status"])

    print("\nAI Generated Answer:")
    print(result["answer"])

    print("\nKnowledge Base Sources:")

    for source in result["sources"]:
        print("-", source)
