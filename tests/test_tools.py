from copilot.agent.tools import search_corpus, open_file, read_chunk


def test_search_corpus_returns_results():
    results = search_corpus("RAG pipeline")
    assert len(results) > 0
    assert "rag" in results.lower()


def test_open_file_markdown():
    content = open_file("01_ai_evals.md")
    assert len(content) > 0
    assert "Evaluation" in content


def test_open_file_not_found():
    result = open_file("nonexistent.md")
    assert "not found" in result.lower()


def test_read_chunk_not_found():
    result = read_chunk("fake::chunk_99")
    assert "not found" in result.lower()