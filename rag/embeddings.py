
from sentence_transformers import SentenceTransformer

# Lightweight embedding model.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load model once and reuse it.
_embedding_model = None


def get_embedding_model():
    global _embedding_model

    if _embedding_model is None:
        print("Loading embedding model...")
        _embedding_model = SentenceTransformer(MODEL_NAME)
        print("Embedding model loaded successfully!")

    return _embedding_model


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Convert multiple text documents into embeddings."""

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True
    )

    return embeddings.tolist()


def generate_query_embedding(text: str) -> list[float]:
    """Convert a user question into an embedding."""

    model = get_embedding_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()
