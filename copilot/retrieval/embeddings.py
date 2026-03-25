import numpy as np
from openai import OpenAI
from copilot.config import settings


client = OpenAI(
    api_key=settings.nvidia_api_key,
    base_url=settings.nvidia_base_url
)


def embed_texts(texts: list[str]) -> np.ndarray:
    response = client.embeddings.create(
        model=settings.embed_model,
        input=texts,
        encoding_format="float",
        extra_body={"input_type": "passage", "truncate": "END"}
    )
    vectors = [item.embedding for item in response.data]
    return np.array(vectors, dtype="float32")


def embed_query(query: str) -> np.ndarray:
    response = client.embeddings.create(
        model=settings.embed_model,
        input=[query],
        encoding_format="float",
        extra_body={"input_type": "query", "truncate": "END"}
    )
    return np.array(response.data[0].embedding, dtype="float32")