from copilot.config import settings


def chunk_text(text: str, file_name: str, file_type: str) -> list[dict]:
    words = text.split()
    chunks = []
    step = settings.chunk_size - settings.chunk_overlap
    chunk_index = 0

    for i in range(0, len(words), step):
        chunk_words = words[i: i + settings.chunk_size]
        if not chunk_words:
            continue
        chunk_text = " ".join(chunk_words)
        chunks.append({
            "chunk_id": f"{file_name}::chunk_{chunk_index}",
            "file": file_name,
            "type": file_type,
            "text": chunk_text,
            "word_count": len(chunk_words)
        })
        chunk_index += 1

    return chunks


def chunk_documents(documents: list[dict]) -> list[dict]:
    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc["text"], doc["file"], doc["type"])
        all_chunks.extend(chunks)
    return all_chunks