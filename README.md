# ReAct Research Copilot

A single-agent research copilot using the **ReAct (Reason + Act)** pattern
to answer questions from a local document corpus with inline citations.

## Architecture

Streamlit UI → FastAPI → ReAct Agent → Tools → Retriever → FAISS → Corpus

## Quick Start

# 1. Clone and enter

git clone <https://github.com/YOUR_USERNAME/react-research-copilot.git>
cd react-research-copilot

# 2. Create and activate virtual environment

python -m venv venv
venv\Scripts\activate

# 3. Install dependencies

make install

# 4. Add your API key

copy .env.example .env

# 5. Build the vector index

make index

# 6. Run the API

make run-api

# 7. Run the UI (new terminal)

make run-ui

## Project Structure

| Folder | Purpose |
|---|---|
| `copilot/` | Main Python package |
| `copilot/agent/` | ReAct loop, prompts, tools |
| `copilot/retrieval/` | Embeddings, vector store, chunking |
| `copilot/ingestion/` | Document parsing pipeline |
| `copilot/api/` | FastAPI routes and schemas |
| `copilot/evaluation/` | Baseline vs ReAct evaluation |
| `frontend/` | Streamlit UI |
| `corpus/` | Source documents |
| `outputs/` | Generated index, logs, runs |
| `scripts/` | Operational scripts |
| `tests/` | Unit tests |
