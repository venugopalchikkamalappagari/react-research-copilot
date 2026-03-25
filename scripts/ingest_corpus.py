import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from copilot.ingestion.ingest_pipeline import load_corpus
from copilot.retrieval.chunking import chunk_documents
from copilot.retrieval.vector_store import build_index, save_index


def main():
    print("Step 1: Loading corpus...")
    documents = load_corpus()
    print(f"Loaded {len(documents)} documents")

    print("\nStep 2: Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")

    print("\nStep 3: Building vector index...")
    index, chunks = build_index(chunks)

    print("\nStep 4: Saving index...")
    save_index(index, chunks)

    print("\nDone! Index is ready.")


if __name__ == "__main__":
    main()