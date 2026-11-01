
import json
from pathlib import Path
from datetime import datetime, timezone


LOG_FILE = Path("logs/performance_metrics.jsonl")


def log_performance(question: str, metrics: dict):

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "model": metrics.get("model"),
        "status": metrics.get("status"),
        "retrieval_time_seconds": metrics.get(
            "retrieval_time_seconds", 0
        ),
        "llm_response_time_seconds": metrics.get(
            "llm_response_time_seconds", 0
        ),
        "ollama_inference_time_seconds": metrics.get(
            "ollama_inference_time_seconds", 0
        ),
        "total_time_seconds": metrics.get(
            "total_time_seconds", 0
        ),
        "prompt_tokens": metrics.get("prompt_tokens", 0),
        "completion_tokens": metrics.get("completion_tokens", 0),
        "total_tokens": metrics.get("total_tokens", 0),
        "external_api_cost": 0
    }

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")

    print("\n[MONITORING] Performance metrics saved.")
