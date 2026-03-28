import json
from pathlib import Path
from copilot.retrieval.vector_store import search, load_index
from copilot.config import settings

# Safe tool allow-list — only these tools can be called by the agent
ALLOWED_TOOLS = {"search_corpus", "open_file", "read_chunk"}


def safe_execute(tool_name: str, tool_args: dict) -> str:
    """Execute a tool only if it is in the allow-list."""
    if tool_name not in ALLOWED_TOOLS:
        return f"Tool '{tool_name}' is not permitted. Allowed tools: {sorted(ALLOWED_TOOLS)}"
    if tool_name not in TOOL_MAP:
        return f"Tool '{tool_name}' is allowed but not implemented."
    try:
        return TOOL_MAP[tool_name](**tool_args)
    except Exception as e:
        return f"Tool '{tool_name}' raised an error: {e}"

# Load index once at startup
_index, _chunks = load_index()


def search_corpus(query: str) -> str:
    results = search(query, _index, _chunks)
    if not results:
        return "No relevant chunks found."
    output = []
    for r in results:
        citation = r.get("citation", f"[{r['file']}]")
        output.append(
            f"{citation}\n{r['text']}\n(score: {r['score']:.4f})"
        )
    return "\n\n---\n\n".join(output)


def open_file(filename: str) -> str:
    corpus_path = Path(settings.corpus_dir) / filename
    if not corpus_path.exists():
        return f"File not found: {filename}"
    suffix = corpus_path.suffix.lower()
    if suffix == ".md":
        return corpus_path.read_text(encoding="utf-8", errors="ignore")
    elif suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(corpus_path))
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append(f"[Page {i}]\n{text.strip()}")
        return "\n\n".join(pages)
    return f"Unsupported file type: {suffix}"


def read_chunk(chunk_id: str) -> str:
    for chunk in _chunks:
        if chunk["chunk_id"] == chunk_id:
            return f"[{chunk['file']}]\n{chunk['text']}"
    return f"Chunk not found: {chunk_id}"


# Tool definitions for the LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_corpus",
            "description": "Search the document corpus for chunks relevant to a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_file",
            "description": "Open and read the full contents of a file from the corpus.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The filename to open e.g. guide_chunking.pdf"
                    }
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_chunk",
            "description": "Read a specific chunk by its chunk_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chunk_id": {
                        "type": "string",
                        "description": "The chunk_id e.g. guide_chunking.pdf::chunk_0"
                    }
                },
                "required": ["chunk_id"]
            }
        }
    }
]


TOOL_MAP = {
    "search_corpus": search_corpus,
    "open_file": open_file,
    "read_chunk": read_chunk
}  