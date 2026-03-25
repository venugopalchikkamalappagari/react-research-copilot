from copilot.ingestion.parser import load_corpus

docs = load_corpus("corpus")

print(f"Loaded {len(docs)} documents\n")

for d in docs[:3]:
    print("File:", d["file"])
    print("Type:", d["type"])
    print("----")