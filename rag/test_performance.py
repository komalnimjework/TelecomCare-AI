
from rag.answer_generator import generate_rag_answer


question = "I cannot connect to the company VPN."

result = generate_rag_answer(question)


print("\n========== RAG PERFORMANCE REPORT ==========")

print("\nQuestion:", question)

print("\nAnswer:")
print(result["answer"])

print("\nSources:")
for source in result["sources"]:
    print("-", source)

print("\nStatus:", result["status"])

print("\n========== PERFORMANCE METRICS ==========")

print("Model:", result["model"])

print("Retrieval Time:",
      result["retrieval_time_seconds"], "seconds")

print("LLM Response Time:",
      result["llm_response_time_seconds"], "seconds")

print("Ollama Inference Time:",
      result["ollama_inference_time_seconds"], "seconds")

print("Total Processing Time:",
      result["total_time_seconds"], "seconds")

print("\n========== TOKEN USAGE ==========")

print("Prompt Tokens:", result["prompt_tokens"])

print("Completion Tokens:", result["completion_tokens"])

print("Total Tokens:", result["total_tokens"])

print("\nTest completed!")
