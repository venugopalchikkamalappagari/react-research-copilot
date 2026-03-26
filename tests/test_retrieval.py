from copilot.retrieval.chunking import chunk_text, chunk_documents


def test_chunk_text_basic():
    chunks = chunk_text("word " * 100, "test.md", "markdown")
    assert len(chunks) > 1
    assert chunks[0]["file"] == "test.md"
    assert "chunk_id" in chunks[0]


def test_chunk_text_short():
    chunks = chunk_text("short text", "test.md", "markdown")
    assert len(chunks) == 1


def test_chunk_documents():
    docs = [
        {"file": "a.md", "type": "markdown", "text": "word " * 100},
        {"file": "b.md", "type": "markdown", "text": "word " * 100}
    ]
    chunks = chunk_documents(docs)
    assert len(chunks) > 2