# ReAct Research Copilot — My Learning Notes

A running cheatsheet of everything I learn while building this project.
Written in simple terms for quick revision.

---

## 1. Project Overview

**What am I building?**
A Research Copilot — an AI agent that answers questions by reading documents
instead of relying on memorized knowledge. It uses two big ideas: RAG and ReAct.

**RAG (Retrieval-Augmented Generation)**

- Instead of the AI guessing, it first searches your documents for relevant info
- Then uses that info to answer — with citations proving where the answer came from
- Two phases:
  - Indexing (done once): read docs → split into chunks → convert to vectors → store
  - Querying (done per question): convert question to vector → find similar chunks → answer

**ReAct (Reason + Act)**

- The AI doesn't just retrieve once and answer
- It thinks step by step:
  - THOUGHT: what do I need to find?
  - ACTION: search for it using a tool
  - OBSERVE: read what came back
  - Repeat until it has enough to answer
- Much smarter than one-shot retrieval

**Architecture (top to bottom):**

```
Streamlit UI        → what the user sees
FastAPI             → the bridge between UI and brain (HTTP API)
ReAct Agent         → the reasoning loop
Tools               → search(), open_file(), read_chunk()
Retriever           → finds relevant chunks using vectors
FAISS Index         → stores all chunk vectors for fast search
Corpus              → the 40 raw documents (source of truth)
```

---

## 2. Folder Structure

```
react-research-copilot/
├── copilot/                  ← main Python package (the brain)
│   ├── __init__.py           ← marks folder as Python package
│   ├── api/                  ← HTTP layer only, no business logic
│   │   ├── __init__.py
│   │   ├── main.py           ← FastAPI app lives here
│   │   ├── schemas.py        ← request/response data models
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── query.py      ← POST /query endpoint
│   │       └── health.py     ← GET /health endpoint
│   ├── agent/                ← the brain
│   │   ├── __init__.py
│   │   ├── react_agent.py    ← ReAct loop logic
│   │   ├── prompts.py        ← all prompt templates
│   │   └── tools.py          ← search, open_file, read_chunk
│   ├── retrieval/            ← get data out (runs every query)
│   │   ├── __init__.py
│   │   ├── embeddings.py     ← text → vectors
│   │   ├── vector_store.py   ← build + query FAISS index
│   │   └── chunking.py       ← split text into chunks
│   ├── ingestion/            ← get data in (runs once)
│   │   ├── __init__.py
│   │   ├── parser.py         ← reads .md and .pdf files
│   │   └── ingest_pipeline.py← orchestrates full ingestion
│   ├── evaluation/           ← baseline vs ReAct comparison
│   │   ├── __init__.py
│   │   └── evaluator.py
│   └── config.py             ← all settings in one place
├── frontend/                 ← Streamlit UI
│   ├── app.py
│   └── components/
│       ├── chat.py
│       └── sidebar.py
├── corpus/                   ← 40 raw documents, read only, in git
├── outputs/                  ← everything generated, gitignored
│   ├── index/                ← FAISS vector index saved here
│   ├── logs/                 ← agent step-by-step logs
│   └── runs/                 ← evaluation CSVs
├── scripts/
│   ├── ingest_corpus.py      ← run once to build index
│   └── run_eval.py           ← run evaluation pipeline
├── notebooks/
│   └── experimentation.ipynb
├── tests/
│   ├── __init__.py
│   ├── test_ingestion.py
│   ├── test_retrieval.py
│   ├── test_tools.py
│   └── test_agent.py
├── .github/
│   └── workflows/
│       └── ci.yml            ← auto-runs tests on every push
├── react_copilot.py          ← CLI entry point
├── Makefile                  ← shortcuts for common commands
├── requirements.txt          ← list of all packages
├── .env                      ← real API key (gitignored, NEVER push)
├── .env.example              ← safe template (on GitHub)
├── .gitignore                ← tells Git what to ignore
├── README.md                 ← project documentation
└── NOTES.md                  ← this file
```

**Why `copilot/` and not `app/`?**
Named after the product. Imports read as `from copilot.agent.react_agent import ReActAgent` — clear and professional.

**Why `ingestion/` and `retrieval/` are separate?**

- `ingestion/` = "get data in" — runs once when building the index
- `retrieval/` = "get data out" — runs on every user query
- Different jobs, different code, different times they run

**Why `outputs/` is gitignored?**
Contains generated files (FAISS index, logs) that are large and
reproducible. No point storing them on GitHub.

**Why `__init__.py` in every folder?**
Tells Python "this folder is a package, not just a folder."
Without it, imports like `from copilot.agent.react_agent import X` break.
Rule: if you will ever write `from this_folder.x import y` — it needs `__init__.py`.

---

## 3. Git — Version Control

**What is Git?**
A tool that tracks every change you make to your code over time.
Like a detailed save history — you can go back to any point.

**What is GitHub?**
The cloud storage for your Git history.
Also your portfolio — recruiters and interviewers look at this.

**One-time machine setup (already done):**

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@email.com"
git config --global core.autocrlf true   # fixes Windows line endings
```

Stored at: `C:\Users\yourname\.gitconfig`
Only run again if you get a new machine.

**The three commands you use constantly:**

```powershell
git add .                        # stage all changed files (put in box)
git commit -m "description"      # take a snapshot (seal the box)
git push                         # upload to GitHub (ship the box)
```

**First-time project setup (already done):**

```powershell
git init
git add .
git commit -m "chore: initial project scaffold"
git branch -M main
git remote add origin https://github.com/YOU/react-research-copilot.git
git push -u origin main
```

**Every step after that — just three lines:**

```powershell
git add .
git commit -m "feat: what you just built"
git push
```

**Commit message conventions:**

- `chore:` → setup, config, no new features
- `feat:`  → new feature added
- `fix:`   → bug fixed
- `docs:`  → documentation only

**When do we commit?**
After every working step. Each commit = one meaningful piece of work completed.

**Important: .env and Git**
Once Git starts tracking a file, .gitignore alone won't stop it.
If .env accidentally gets tracked, remove it with:

```powershell
git rm --cached .env
```

This removes it from Git tracking WITHOUT deleting it from your computer.

---

## 4. Virtual Environment

**The problem it solves:**
Different projects need different versions of the same packages.
Without isolation, they conflict and break each other.

**What it is:**
An isolated copy of Python created specifically for one project.
Has its own Python, pip, and packages folder.

**Simple analogy:**

- Global Python = your house kitchen (shared, don't mess it up)
- Virtual environment = a portable camping kitchen just for this project

**The commands:**

```powershell
# Create (once per project)
python -m venv venv

# Activate (every time you open a new terminal)
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# Deactivate (when switching projects)
deactivate
```

**How to know it's active:**
Your terminal prompt starts with `(venv)`:

```
(venv) PS D:\ai-projects\react-research-copilot>
```

Always check for this before running any Python command.

**Why venv/ is gitignored:**

- It's 200-500 MB
- Contains OS-specific compiled files
- Anyone can recreate it: `pip install -r requirements.txt`

**The analogy:**

- `requirements.txt` = ingredients list (push to GitHub)
- `venv/` = the cooked meal (don't push, share the recipe)

**Windows-specific: Execution Policy fix (already done)**
If you see "running scripts is disabled", run once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**If venv ever breaks:**

```powershell
rm -rf venv
python -m venv venv
pip install -r requirements.txt
```

---

## 5. NVIDIA NIM — AI Models

**What is NVIDIA NIM?**
NVIDIA's platform for accessing AI models via API.
Uses the same format as the OpenAI API — so you use the `openai`
Python package but point it at NVIDIA's servers instead.

**Three types of models on NIM:**

| Type | Hosted by | Cost | Needs GPU? |
|---|---|---|---|
| Free Endpoint | NVIDIA servers | Free (rate limited) | No |
| Downloadable | Your machine | Hardware cost | Yes — powerful GPU |
| Partner Endpoint | 3rd party | Paid | No |

**For our project — Free Endpoints only:**
No cost, no GPU needed, just an API key. Perfect for a capstone.

**Models we're using:**

| Role | Model | Why |
|---|---|---|
| LLM (reasoning) | `qwen/qwen3.5-122b-a10b` | Best open-source tool calling, agent-ready, free endpoint |
| Embeddings (RAG) | `nvidia/llama-nemotron-embed-1b-v2` | Purpose-built for document QA retrieval, free endpoint |

**Why Qwen3.5 for the ReAct agent?**

- 122B total parameters, only 10B active (MoE = fast)
- Highest tool-calling benchmark score among open models
- Has a reasoning mode — perfect for ReAct's Thought steps
- Free endpoint

**What is MoE (Mixture of Experts)?**
A large model split into "experts" — specialized sub-networks.
Only a few experts activate per query instead of the whole model.
Result: 122B parameter capability at 10B parameter speed.

**API key:**
Stored in `.env` as `NVIDIA_API_KEY=nvapi-...`
Get it from: build.nvidia.com → profile → API Keys

**How the code will use it:**

```python
from openai import OpenAI

client = OpenAI(
    api_key="nvapi-...",
    base_url="https://integrate.api.nvidia.com/v1"
)
```

Same OpenAI package, different base_url. That's it.

---

## 6. Config Files Explained

**`requirements.txt`**
List of all packages the project needs with minimum versions.
`>=0.25.0` means "this version or higher" — flexible but bounded.
Run `pip install -r requirements.txt` to install everything at once.

**`.env`**
Stores secret values — API keys, passwords.
NEVER commit to GitHub. Protected by `.gitignore`.

```
NVIDIA_API_KEY=nvapi-your-key-here
```

**`.env.example`**
Safe template of `.env` — no real values, just placeholders.
Goes to GitHub so others know what keys they need.

```
NVIDIA_API_KEY=your_key_here
```

**`.gitignore`**
Tells Git what to never track or push:

- `venv/` — too large, OS-specific
- `.env` — contains real secrets
- `outputs/` — generated files, reproducible
- `__pycache__/` — Python cache, meaningless in git

**`Makefile`**
Shortcuts for long commands:

```
make install    → pip install -r requirements.txt
make index      → python scripts/ingest_corpus.py
make run-api    → uvicorn copilot.api.main:app --reload ...
make run-ui     → streamlit run frontend/app.py
make evaluate   → python scripts/run_eval.py
make test       → pytest tests/ -v
```

Indented lines must use TAB not spaces — Makefile quirk.

**`ci.yml` (.github/workflows/)**
GitHub automatically runs tests on every push.
Spins up a fresh Linux machine, installs packages, runs pytest.
Shows green checkmark on your GitHub repo if tests pass.

**`README.md`**
Front page of your GitHub repo.
Written in Markdown (.md) — GitHub renders it as formatted page.
Tells visitors: what it is, how to run it, how it's structured.

---

## 7. Packages Installed

| Package | Job in our project |
|---|---|
| `openai` | Talk to NVIDIA NIM API (OpenAI-compatible format) |
| `faiss-cpu` | Store and search vectors fast |
| `numpy` | Math library — vectors are numpy arrays |
| `sentence-transformers` | Convert text to vectors locally (fallback) |
| `pypdf` | Read PDF files from corpus |
| `pandas` | Read evaluation_questions.csv |
| `fastapi` | Build the HTTP API |
| `uvicorn` | Serve the FastAPI app |
| `pydantic` | Validate request/response data shapes |
| `pydantic-settings` | Load settings from .env file |
| `streamlit` | Build the chat UI in pure Python |
| `tqdm` | Progress bars during indexing |
| `rich` | Pretty colored terminal output for agent logs |
| `python-dotenv` | Load .env file into environment on startup |

---

## 8. Key Concepts Glossary

| Term | Simple Explanation |
|---|---|
| **Vector** | A list of numbers representing the meaning of text |
| **Embedding** | Converting text into a vector |
| **FAISS** | Library that stores vectors and finds similar ones fast |
| **Chunk** | A small piece of a document (e.g. 300 words) |
| **RAG** | Find relevant chunks before answering |
| **ReAct** | Loop: Thought → Action → Observe → repeat |
| **MoE** | Mixture of Experts — large model, only part activates per query |
| **NIM** | NVIDIA's platform for hosted AI model APIs |
| **FastAPI** | Python framework for building HTTP APIs |
| **Streamlit** | Python library for building simple web UIs |
| **Pydantic** | Validates that data has the right shape and types |
| **`__init__.py`** | Empty file that makes a folder a Python package |
| **Virtual env** | Isolated Python environment for one project |
| **Git** | Local version control — tracks changes on your machine |
| **GitHub** | Cloud storage for Git history — also your portfolio |
| **CI/CD** | Automatic testing triggered by git push |
| **Makefile** | Shortcuts for long commands |
| **Free Endpoint** | Model hosted by NVIDIA, free with rate limits |
| **Downloadable** | Model you run locally — needs a powerful GPU |
| **Partner Endpoint** | Model hosted by 3rd party, usually paid |

---

## 9. Daily Workflow

```powershell
# Every time you open the project:
cd D:\ai-projects\bia-capstone-projects\react-research-copilot
venv\Scripts\activate            # always first — check for (venv)

# After finishing a step:
git add .
git commit -m "feat: what you built"
git push
```

---

## 10. Build Progress

```
✅ Step 0  — Project scaffold, Git, venv, packages, GitHub push
⬜ Step 1  — Ingestion (parser.py, ingest_pipeline.py)
⬜ Step 2  — Retrieval (chunking.py, embeddings.py, vector_store.py)
⬜ Step 3  — Tools (tools.py)
⬜ Step 4  — ReAct Agent (prompts.py, react_agent.py)
⬜ Step 5  — API (main.py, schemas.py, routes/)
⬜ Step 6  — Frontend (app.py, components/)
⬜ Step 7  — Evaluation (evaluator.py, run_eval.py)
⬜ Step 8  — CLI (react_copilot.py)
⬜ Step 9  — Notebook (experimentation.ipynb)
⬜ Step 10 — Presentation deck
```

---

*Last updated: Step 0 complete — Project scaffold pushed to GitHub*
