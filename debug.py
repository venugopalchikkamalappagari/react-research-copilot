from copilot.ingestion.ingest_pipeline import load_corpus
from copilot.retrieval.chunking import chunk_documents

docs = load_corpus()
print("Documents loaded:", len(docs))

chunks = chunk_documents(docs)
print("Chunks created:", len(chunks))

print("\nWord count per document:")
for d in docs:
    words = len(d["text"].split())
    print(f"  {d['file']} — {words} words")