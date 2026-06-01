# Distill — RAG Document Summarizer

Upload PDFs and PowerPoint files and receive a compact, AI-generated summary PDF.

## Stack

- **Backend:** FastAPI, ChromaDB, sentence-transformers, Ollama (OpenAI-compatible)
- **Frontend:** React, Vite, Material UI

## Prerequisites

- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.ai) with a model pulled (default: `llama3`), or OpenAI API credentials

## Quick start

### 1. Python environment

```bash
cd d:\Projects\Summarag
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
```

### 2. Backend configuration

```bash
copy backend\.env.example backend\.env
# Edit backend\.env if using OpenAI instead of Ollama
```

### 3. Start backend

```bash
cd backend
..\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

### 4. Start frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, upload PDF/PPTX files, optionally set a focus area, and click **Generate Summary PDF**.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/ingest` | Upload and index documents |
| POST | `/api/summarize` | Generate summary PDF |
| GET | `/api/download/{filename}` | Download generated PDF |

## Tests

```bash
cd backend
..\.venv\Scripts\pytest tests/ -v
```

All tests use mocked LLM and ChromaDB — no live Ollama or Hugging Face calls during CI.

## Project layout

```
Summarag/
├── backend/          # FastAPI app, services, tests
├── frontend/         # React + MUI UI
├── .venv/            # Python virtual environment (gitignored)
└── README.md
```

## Environment variables

See `backend/.env.example` for `LLM_BASE_URL`, `LLM_MODEL`, chunk sizes, and storage paths.
