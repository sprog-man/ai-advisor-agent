# AI Advisor Agent — Project Guide

> Auto-loaded by Claude Code. Read this first in every new session.

## Quick Start

```bash
# 1. Activate venv
source .venv/Scripts/activate        # Windows/bash
# .venv\Lib\Scripts\activate         # Windows cmd/powershell

# 2. Run CLI
python main.py

# 3. Load knowledge base (one-time init)
python scripts/load_documents.py
```

## Architecture Overview

```
User Input ──→ IntentAgent ──→ retrieve(KnowledgeRetriever) ──→ DecomposeAgent ──→ SummaryAgent ──→ Output
                  │                        │                           │
             Structured              RAG search                   Structured
             IntentSchema              in ChromaDB                  PlanSchema
```

### Core Data Flow

1. **IntentAgent** — Parses user input into `IntentSchema` (objective, domain, constraints, complexity)
2. **retrieve** — Searches `data/chroma_db/ai_knowledge/` via similarity search, injects context into `knowledge_context`
3. **DecomposeAgent** — Breaks intent into ordered `PlanSchema` steps with dependencies, aware of retrieved knowledge
4. **SummaryAgent** — Formats plan into friendly natural-language response

### Global State (`state/agent_state.py`)

| Field | Type | Description |
|---|---|---|
| `messages` | `Annotated[List[dict], add_messages]` | Conversation history (auto-appended by LangGraph) |
| `user_intent` | `str` | Structured intent from IntentAgent |
| `plan` | `List[dict]` | Task steps with id, description, dependencies, status |
| `knowledge_context` | `str` | Retrieved KB context injected into DecomposeAgent prompt |
| `final_summary` | `str` | Final formatted output |
| `error_count` | `int` | Retry counter |
| `max_retries` | `int` | Max retries (default 3) |
| `current_checkpoint_id` | `Optional[str]` | LangGraph checkpoint ID |
| `status` | `str` | running / success / failed / paused |

## Module Map

| Directory | Purpose | Key Files |
|---|---|---|
| `config/` | Settings & env | `settings.py` — Pydantic config, loads from `.env` |
| `core/` | Infrastructure | `llm_factory.py` — `create_llm()` returns ChatOpenAI, `call_llm()` returns str |
| `state/` | Type definitions | `agent_state.py` — AgentState TypedDict, `schemas.py` — Pydantic schemas |
| `agents/` | Business logic | `intent_agent.py`, `decompose_agent.py`, `summary_agent.py` |
| `graph/` | Orchestration | `main_graph.py` — StateGraph definition, node wiring, edges |
| `rag/` | Knowledge base | `document_loader.py` (PDF/DOCX/MD), `text_splitter.py` (smart chunking), `retrieve.py` (ChromaDB) |
| `scripts/` | Utilities | `load_documents.py` — one-shot KB ingestion |
| `data/` | Runtime data | `knowledge_base/` (source docs), `chroma_db/` (vector store, gitignored) |

## Known Issues & Gotchas

### Dependency Version Conflicts
- `langgraph-checkpoint-sqlite` package versions jumped from 0.x to 1.x — `requirements.txt` must pin to `>=1.0.0`, not `<0.3.0`. Use `langgraph-checkpoint-sqlite>=1.0.0`.

### SqliteSaver 3.x API
- `langgraph-checkpoint-sqlite>=3.0.0` removed `from_conn_string()` — use `SqliteSaver(sqlite3.connect(db_path, check_same_thread=False))` directly
- `main.py` must pass `config={'configurable': {'thread_id': '...'}}` to `app.invoke()` to activate checkpointing; otherwise checkpoint is unused
- `initial_state` for each turn only needs `{"messages": [...]}` (checkpoint loads the rest)

### LangChain 1.x Migration
- `langchain.schema.Document` → `langchain_core.documents.Document`
- `langchain.text_splitter` → `langchain_text_splitters`
- `RunnableSequence` is NOT callable — use `.invoke()`, not `()`
- `call_llm()` returns `str`, NOT a runnable — use `create_llm()` for `.with_structured_output()`

### Embedding API (Gitee / Qwen3-Embedding-0.6B)
- Must set `check_embedding_ctx_length=False` — otherwise langchain sends token IDs instead of text, causing 400 error
- Must set `chunk_size=10` in `OpenAIEmbeddings` — batch sizes >10 cause schema validation errors on Gitee
- `encoding_format` and `dimensions` params may not be supported

### Windows Console Encoding
- GBK encoding breaks emoji prints (e.g., `\U0001f916`). Fixed by removing emojis from banner/print statements
- Set `PYTHONIOENCODING=utf-8` env var if printing UTF-8 to console is needed

### RAG Search Quality
- `Qwen3-Embedding-0.6B` has limited Chinese semantic discrimination — consider upgrading to `text-embedding-v3` or OpenAI embeddings
- Chunk size 1000 chars may fragment long technical descriptions — tune if retrieval misses relevant content

## Current Status

| Phase | Status | Commit |
|---|---|---|
| Phase 1: Core Skeleton | Done | `ee98eeb` |
| Phase 2: RAG Knowledge Base | Done | `5f70f4c` |
| Phase 3: Short-term Memory + Checkpoint | In Progress | — |
| Phase 4: Long-term Memory (3-layer) | Pending | — |
| Phase 5: Reflection + Multi-Agent | Pending | — |
| Phase 6: Feedback Loop + Production | Pending | — |

## Git Strategy

- **Remote:** `https://github.com/sprog-man/ai-advisor-agent.git`
- **Branches:** `main` (stable) → `develop` → `phase/N-*` feature branches
- **Convention:** `feat:`, `fix:`, `refactor:`, `docs:`, `test:` prefixes
- **Gitignored:** `.env`, `data/chroma_db/`, `__pycache__/`, `.venv/`

## Dependencies

Key packages (see `requirements.txt`):
- `langgraph>=0.2.0`, `langchain>=0.3.0`, `langchain-openai>=0.2.0`
- `langgraph-checkpoint-sqlite>=1.0.0`, `langchain-text-splitters>=0.3.0`, `langchain-chroma>=0.2.0`
- `openai>=1.0.0`, `chromadb>=0.5.0`
- `PyMuPDF>=1.24.0`, `python-docx>=1.1.0`
- `python-dotenv>=1.0.0`, `pydantic>=2.0.0`

## Debugging Checklist

When something breaks, check in this order:

1. **Import errors** → Are you in the activated `.venv`? Is Python interpreter pointing to `.venv` in VS Code?
2. **LLM errors** → Is `.env` configured? Does `create_llm()` work standalone?
3. **Embedding errors** → `check_embedding_ctx_length=False`? `chunk_size=10`?
4. **RAG empty results** → Did you run `python scripts/load_documents.py`? Is `data/chroma_db/ai_knowledge/chroma.sqlite3` populated?
5. **Agent returns fallback** → Check traceback in `except` blocks — what error caused the fallback?
6. **Graph wiring** → Is the edge order correct in `main_graph.py`? Did you forget to add a new node?
7. **Checkpoint not working** → Is `config` passed to `app.invoke()`? Is `SqliteSaver` created with a `sqlite3.Connection` directly (not `from_conn_string`)?
