# Distill — RAG Document Summarizer

Upload PDFs and PowerPoint files and receive a compact, AI-generated summary PDF.

## Stack

- **Backend:** FastAPI, ChromaDB, sentence-transformers
- **LLM:** ChatGPT (OpenAI), Google Gemini, or local Ollama — configured via `.env`
- **Frontend:** React, Vite, Material UI (modern dark UI with glassmorphism)

## Prerequisites

- Python 3.11+
- Node.js 20+
- An API key for **ChatGPT** or **Gemini**, or a local [Ollama](https://ollama.ai) install

## Quick start

### 1. Python environment

```bash
cd d:\Projects\Summarag
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
```

### 2. Configure LLM (required for summarization)

```bash
copy .env.example .env
```

Edit `.env` and choose a provider:

| Provider | Set in `.env` | API key variable |
|----------|---------------|------------------|
| **ChatGPT** | `LLM_PROVIDER=openai` | `OPENAI_API_KEY` from [OpenAI](https://platform.openai.com/api-keys) |
| **Gemini** | `LLM_PROVIDER=gemini` | `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com/apikey) |
| **Ollama** (local) | `LLM_PROVIDER=ollama` | No key — run `ollama pull llama3` |

Example (ChatGPT):

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

Example (Gemini):

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key-here
GEMINI_MODEL=gemini-2.0-flash
```

Environment files are loaded from the repo root `.env` and/or `backend/.env` (backend overrides root).

### 3. Start backend

```bash
cd backend
..\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

Check configuration: `GET http://localhost:8000/health` returns `provider` and `model`.

### 4. Start frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the UI shows API/LLM status in the header, supports drag-and-drop upload, a live pipeline stepper, and an in-app summary preview before download.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check + active LLM provider/model |
| POST | `/api/ingest` | Upload and index documents |
| POST | `/api/summarize` | Generate summary PDF |
| GET | `/api/download/{filename}` | Download generated PDF |

## Tests

```bash
cd backend
..\.venv\Scripts\pytest tests/ -v
```

All tests use mocked LLM and ChromaDB — no real API keys or network calls during tests.

## Project layout

```
Summarag/
├── .env.example          # LLM + app config template (copy to .env)
├── backend/              # FastAPI app, services, tests
├── frontend/             # React + MUI UI
├── .venv/                # Python virtual environment (gitignored)
└── README.md
```

## Environment variables

See [`.env.example`](.env.example) for all options: `LLM_PROVIDER`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, chunk sizes, and storage paths.
