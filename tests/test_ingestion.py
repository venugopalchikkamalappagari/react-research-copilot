from copilot.ingestion.parser import parse_markdown, parse_pdf
from copilot.ingestion.ingest_pipeline import load_corpus
from pathlib import Path


def test_parse_markdown():
    doc = parse_markdown(Path("corpus/01_ai_evals.md"))
    assert doc["type"] == "markdown"
    assert len(doc["text"]) > 0
    assert doc["file"] == "01_ai_evals.md"


def test_parse_pdf():
    doc = parse_pdf(Path("corpus/guide_chunking.pdf"))
    assert doc["type"] == "pdf"
    assert len(doc["text"]) > 0


def test_load_corpus():
    docs = load_corpus()
    assert len(docs) == 39
    types = [d["type"] for d in docs]
    assert "markdown" in types
    assert "pdf" in types