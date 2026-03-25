import faiss
import numpy as np
import json
from pathlib import Path
from tqdm import tqdm
from copilot.config import settings
from copilot.retrieval.embeddings import embed_texts, embed_query


BATCH_SIZE = 16


def build_index(chunks: list[dict]) -> tuple:
    texts = [c["text"] for c in chunks]
    all_vectors = []

    for i in tqdm(range(0, len(texts), BATCH_SIZE), desc="Embedding chunks"):
        batch = texts[i: i + BATCH_SIZE]
        vectors = embed_texts(batch)
        all_vectors.append(vectors)

    matrix = np.vstack(all_vectors)
    dim = matrix.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(matrix)
    return index, chunks


def save_index(index, chunks: list[dict]):
    index_dir = Path(settings.index_dir)
    index_dir.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_dir / "faiss.index"))
    with open(index_dir / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Saved index with {index.ntotal} vectors")


def load_index() -> tuple:
    index_dir = Path(settings.index_dir)
    index = faiss.read_index(str(index_dir / "faiss.index"))
    with open(index_dir / "chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)
    return index, chunks


def search(query: str, index, chunks: list[dict]) -> list[dict]:
    query_vector = embed_query(query)
    query_vector = np.expand_dims(query_vector, axis=0)
    distances, indices = index.search(query_vector, settings.top_k)
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        chunk = chunks[idx].copy()
        chunk["score"] = float(dist)
        results.append(chunk)
    return results