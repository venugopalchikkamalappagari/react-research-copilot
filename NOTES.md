# ReAct Research Copilot — My Learning Notes

A running cheatsheet of everything I learned while building this project.
Written in simple terms for quick revision.

---

## 1. Project Overview

**What I built:**
A Research Copilot — an AI agent that answers questions by reading documents
instead of relying on memorized knowledge. Uses two big ideas: RAG and ReAct.

**RAG (Retrieval-Augmented Generation)**

- Instead of the AI guessing, it first searches your documents for relevant info
- Then uses that info to answer — with citations proving where the answer came from
- Two phases:
  - Indexing (done once): read docs → split into chunks → convert to vectors → store
  - Querying (per question): convert question to vector → find similar chunks → answer

**ReAct (Reason + Act)**

- The AI doesn't just retrieve once and answer
- It thinks step by step:
  - THOUGHT: what do I need to find?
  - ACTION: search for it using a tool
  - OBSERVE: read what came back
  - Repeat until it has enough to answer

**Architecture:**

```
Streamlit UI → FastAPI → ReAct Agent → Tools → Retriever → FAISS Index → Corpus
```

---

## 2. Folder Structure

```
react-research-copilot/
├── copilot/                  ← main Python package
│   ├── api/                  ← FastAPI routes and schemas
│   │   ├── main.py           ← FastAPI app
│   │   ├── schemas.py        ← request/response models
│   │   └── routes/
│   │       ├── query.py      ← POST /query
│   │       └── health.py     ← GET /health
│   ├── agent/                ← the brain
│   │   ├── react_agent.py    ← ReAct loop with timeout + retry
│   │   ├── prompts.py        ← all prompt templates
│   │   └── tools.py          ← search, open_file, read_chunk + allow-list
│   ├── retrieval/            ← RAG pipeline
│   │   ├── embeddings.py     ← text → vectors (NVIDIA NIM)
│   │   ├── vector_store.py   ← build + query FAISS
│   │   └── chunking.py       ← split docs into chunks with page tracking
│   ├── ingestion/            ← document parsing
│   │   ├── parser.py         ← reads .md and .pdf files
│   │   └── ingest_pipeline.py
│   ├── evaluation/
│   │   └── evaluator.py      ← baseline vs ReAct + report generator
│   └── config.py             ← all settings (pydantic-settings)
├── frontend/
│   ├── app.py                ← Streamlit chat UI
│   └── components/
├── corpus/                   ← 39 raw documents (read-only)
├── outputs/                  ← gitignored
│   ├── index/                ← FAISS index (faiss.index + chunks.json)
│   ├── logs/
│   └── runs/                 ← eval CSVs + evaluation_report.md
├── scripts/
│   ├── ingest_corpus.py      ← builds the vector index
│   ├── run_eval.py           ← runs baseline + ReAct evaluation
│   └── generate_report.py    ← generates evaluation_report.md from CSVs
├── notebooks/
│   └── experimentation.ipynb ← full pipeline walkthrough
├── tests/                    ← 12 unit tests, all passing
├── .github/workflows/ci.yml  ← auto-runs tests on every push
├── react_copilot.py          ← CLI entry point
├── Makefile                  ← shortcuts
├── requirements.txt
├── .env                      ← real API key (gitignored)
├── .env.example
├── .gitignore
└── README.md
```

---

## 3. Git — Version Control

**What is Git?**
Tracks every change you make to code over time. Like a detailed save history.

**What is GitHub?**
Cloud storage for Git history. Also your portfolio.

**One-time machine setup (already done):**

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@email.com"
git config --global core.autocrlf true
```

**The three commands you use constantly:**

```powershell
git add .                        # stage all changes
git commit -m "description"      # take a snapshot
git push                         # upload to GitHub
```

**Commit message conventions:**

- `chore:` → setup, config
- `feat:`  → new feature
- `fix:`   → bug fixed
- `docs:`  → documentation

**If .env gets accidentally tracked:**

```powershell
git rm --cached .env
```

---

## 4. Virtual Environment

**Commands:**

```powershell
python -m venv venv              # create (once)
venv\Scripts\activate            # activate (every new terminal)
deactivate                       # deactivate
```

**Always check for `(venv)` in terminal before running anything.**

**Windows execution policy fix (already done):**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**If venv breaks:**

```powershell
rm -rf venv
python -m venv venv
pip install -r requirements.txt
```

---

## 5. NVIDIA NIM — AI Models

**What:** NVIDIA's hosted AI model API. Uses OpenAI-compatible format.

**Three types:**

| Type | Cost | Needs GPU? |
|---|---|---|
| Free Endpoint | Free (rate limited) | No |
| Downloadable | Hardware cost | Yes |
| Partner Endpoint | Paid | No |

**Models we used:**

| Role | Model |
|---|---|
| LLM | `meta/llama-3.1-8b-instruct` |
| Embeddings | `nvidia/llama-nemotron-embed-1b-v2` |

**Why llama-3.1-8b over Qwen3.5-122B?**
Qwen was 94s per response. Llama 8B was 3.8s. 25x faster. Same quality for this corpus.

**How the code uses it:**

```python
from openai import OpenAI
client = OpenAI(
    api_key="nvapi-...",
    base_url="https://integrate.api.nvidia.com/v1"
)
```

**Embedding model requires input_type:**

```python
# For indexing documents
extra_body={"input_type": "passage", "truncate": "END"}

# For querying
extra_body={"input_type": "query", "truncate": "END"}
```

This is called an asymmetric embedding model — different representations for documents vs queries.

---

## 6. RAG Pipeline — How It Works

**Step 1: Ingestion**

```
parser.py reads .md and .pdf files → returns {file, type, text, pages}
```

**Step 2: Chunking**

```
chunking.py splits text into ~50 word chunks
PDFs are chunked per-page so page numbers are preserved
Each chunk stores: chunk_id, file, type, page, citation, text
```

**Citation format:**

- Markdown: `[01_rag.md]`
- PDF: `[guide_chunking.pdf:1]`  ← page number included

**Step 3: Embedding**

```
embeddings.py converts each chunk text → vector (list of numbers)
Uses NVIDIA's embed model via API
Vectors stored as numpy float32 arrays
```

**Step 4: FAISS Index**

```
vector_store.py builds a FAISS IndexFlatL2
Stores all vectors + saves chunks.json alongside
Batch size 16 to respect rate limits
```

**Step 5: Retrieval**

```
User question → embed_query() → FAISS search → top-5 nearest chunks
Lower L2 distance = more similar = better match
```

---

## 7. ReAct Agent — How It Works

**The loop:**

```python
for step in range(max_steps):          # max 8 steps
    response = LLM(messages, tools)    # LLM decides what to do
    if no tool call:
        final_answer = response        # done
        break
    else:
        observation = execute_tool()   # run the tool
        messages.append(observation)   # feed back to LLM
        continue                       # next step
```

**Guardrails built in:**

- `max_react_steps = 8` — prevents infinite loops
- `timeout = 60s` — per API call timeout
- Retry with backoff — 3 attempts, 5s/10s/15s waits
- Safe tool allow-list — only permitted tools can execute

**Safe tool allow-list:**

```python
ALLOWED_TOOLS = {"search_corpus", "open_file", "read_chunk"}

def safe_execute(tool_name, tool_args):
    if tool_name not in ALLOWED_TOOLS:
        return f"Tool '{tool_name}' is not permitted."
    return TOOL_MAP[tool_name](**tool_args)
```

**Tools available:**

| Tool | What it does |
|---|---|
| `search_corpus(query)` | Vector search → top 5 chunks |
| `open_file(filename)` | Read full file from corpus |
| `read_chunk(chunk_id)` | Read one specific chunk |

---

## 8. FastAPI — The HTTP Layer

**Why FastAPI between UI and agent?**

- Separation of concerns — UI has no business logic
- Any frontend (Streamlit, React, mobile) can use the same API
- Pydantic validates every request before it reaches the agent

**Endpoints:**

```
GET  /health  → {"status": "ok", "message": "..."}
POST /query   → {"question": "..."} → {"answer": "...", "steps": [...]}
```

**How to run:**

```powershell
uvicorn copilot.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Swagger docs:** <http://localhost:8000/docs>

---

## 9. Streamlit UI

**How to run:**

```powershell
streamlit run frontend/app.py
```

**Features built:**

- Chat interface with history
- Agent steps expandable panel (Thought / Action / Observe)
- Response time display
- API health check in sidebar

**Important:** Don't run Streamlit and evaluation at the same time — they compete for the same NVIDIA API rate limit (40 RPM).

---

## 10. Evaluation

**Metric: Grounded Precision**

```
Word overlap between agent answer and gold snippet
Range: 0.0 (no overlap) to 1.0 (perfect overlap)
```

**Results:**

| Mode | Grounded Precision |
|---|---|
| Baseline (no tools) | 0.36 |
| ReAct + tools | 0.57 |
| Improvement | +0.20 (56% relative gain) |

**Manual accuracy (sampled 10 questions): ~0.80**

**Key failure cases:**

- Q02: Wrong chunks retrieved for prompt injection → answer drifted
- Q05: Gold snippet wording not in any chunk → corpus coverage gap
- Q15/Q16: Agent answer correct but used different wording than gold snippet

**How to run evaluation:**

```powershell
python scripts/run_eval.py           # runs both modes, saves CSVs
python scripts/generate_report.py   # generates evaluation_report.md
```

---

## 11. Key Concepts Glossary

| Term | Simple Explanation |
|---|---|
| **Vector** | List of numbers representing meaning of text |
| **Embedding** | Converting text into a vector |
| **FAISS** | Library that stores vectors and finds similar ones fast |
| **Chunk** | Small piece of a document (~50 words) |
| **RAG** | Find relevant chunks before answering |
| **ReAct** | Loop: Thought → Action → Observe → repeat |
| **MoE** | Mixture of Experts — large model, only part activates |
| **Asymmetric embedding** | Different vectors for documents vs queries |
| **Grounded precision** | Word overlap between answer and gold snippet |
| **Allow-list** | Explicit list of permitted operations |
| **FastAPI** | Python framework for building HTTP APIs |
| **Streamlit** | Python library for building web UIs |
| **Pydantic** | Validates data shapes and types |
| **`__init__.py`** | Makes a folder importable as Python package |
| **Virtual env** | Isolated Python environment for one project |
| **Git** | Local version control |
| **GitHub** | Cloud storage for Git history + portfolio |
| **CI/CD** | Auto-runs tests on every push |
| **Makefile** | Shortcuts for long commands |
| **Free Endpoint** | NVIDIA-hosted model, free with rate limits |

---

## 12. Daily Workflow

```powershell
# Start of every session:
cd D:\ai-projects\bia-capstone-projects\react-research-copilot
venv\Scripts\activate

# Run the full stack:
# Terminal 1 — build index (once)
python scripts/ingest_corpus.py

# Terminal 2 — start API
uvicorn copilot.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3 — start UI
streamlit run frontend/app.py

# Terminal 4 — CLI test
python react_copilot.py --question "What is a North Star metric?"

# After finishing work:
git add .
git commit -m "feat/fix/docs: description"
git push
```

---

## 13. Make Commands

```powershell
make install    # pip install -r requirements.txt
make index      # python scripts/ingest_corpus.py
make run-api    # uvicorn copilot.api.main:app --reload ...
make run-ui     # streamlit run frontend/app.py
make evaluate   # python scripts/run_eval.py
make test       # pytest tests/ -v
```

---

## 14. Build Progress — COMPLETE

```
✅ Step 0  — Scaffold, Git, venv, packages, GitHub
✅ Step 1  — Ingestion (parser.py, ingest_pipeline.py)
✅ Step 2  — Retrieval (chunking with page tracking, embeddings, FAISS)
✅ Step 3  — Tools (search_corpus, open_file, read_chunk, allow-list)
✅ Step 4  — ReAct Agent (prompts, loop, timeout, retry, allow-list)
✅ Step 5  — FastAPI (routes, schemas, CORS middleware)
✅ Step 6  — Streamlit UI (chat, agent steps, response timing)
✅ Step 7  — Evaluation (baseline 0.36 vs ReAct 0.57, +56%)
✅ Step 8  — CLI (react_copilot.py --question "...")
✅ Step 9  — Jupyter Notebook (full pipeline walkthrough)
✅ Step 10 — Presentation deck (9 slides, dark visual theme)

✅ Gap 1   — PDF citations now [file:page]
✅ Gap 2   — Agent prompt requires supporting quotes
✅ Gap 3   — Written evaluation report (evaluation_report.md)
✅ Gap 4   — Manual accuracy ~0.80 in report
✅ Gap 5   — Timeout in agent loop (60s per call)
✅ Gap 6   — Retry with backoff in main agent (3 attempts)
✅ Gap 7   — Safe tool allow-list (safe_execute)
```

---

## 15. Resume Bullet Points

```
ReAct Research Copilot                    Python, FastAPI, Streamlit, FAISS
• Built a multi-step ReAct agent with RAG over a 39-document corpus
• Designed FastAPI service exposing agent endpoints with Pydantic validation
• Implemented FAISS vector index with NVIDIA NIM embedding model
• Added guardrails: max-steps, 60s timeout, retry with backoff, safe tool allow-list
• Evaluated grounded precision: baseline 0.36 → ReAct 0.57 (+56%) on 20 questions
• Deployed interactive Streamlit UI with real-time agent step tracing and citations
```

---

*Project complete. Submitted: March 2026*
