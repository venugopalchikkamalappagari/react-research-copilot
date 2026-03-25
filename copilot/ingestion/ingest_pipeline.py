from pathlib import Path
from tqdm import tqdm
from copilot.ingestion.parser import parse_file


def load_corpus(corpus_dir: str = "corpus") -> list[dict]:
    corpus_path = Path(corpus_dir)
    files = list(corpus_path.glob("*.*"))
    documents = []
    for file_path in tqdm(files, desc="Loading corpus"):
        doc = parse_file(file_path)
        if doc:
            documents.append(doc)
    return documents


if __name__ == "__main__":
    docs = load_corpus()
    print(f"\nLoaded {len(docs)} documents")
    for d in docs[:3]:
        print(f"  {d['file']} ({d['type']}) — {len(d['text'])} chars")