from copilot.config import settings


def chunk_text(text: str, file_name: str, file_type: str, page: int = None) -> list[dict]:
    words = text.split()
    chunks = []
    step = settings.chunk_size - settings.chunk_overlap
    chunk_index = 0

    for i in range(0, len(words), step):
        chunk_words = words[i: i + settings.chunk_size]
        if not chunk_words:
            continue

        # Build citation string
        if file_type == "pdf" and page is not None:
            citation = f"[{file_name}:{page}]"
        else:
            citation = f"[{file_name}]"

        chunks.append({
            "chunk_id": f"{file_name}::chunk_{chunk_index}",
            "file": file_name,
            "type": file_type,
            "page": page,
            "citation": citation,
            "text": " ".join(chunk_words),
            "word_count": len(chunk_words)
        })
        chunk_index += 1

    return chunks


def chunk_documents(documents: list[dict]) -> list[dict]:
    all_chunks = []
    for doc in documents:
        if doc["type"] == "pdf" and "pages" in doc:
            # Chunk each page separately to preserve page numbers
            for page_data in doc["pages"]:
                if not page_data["text"].strip():
                    continue
                chunks = chunk_text(
                    page_data["text"],
                    doc["file"],
                    doc["type"],
                    page=page_data["page"]
                )
                all_chunks.extend(chunks)
        else:
            chunks = chunk_text(doc["text"], doc["file"], doc["type"])
            all_chunks.extend(chunks)
    return all_chunks