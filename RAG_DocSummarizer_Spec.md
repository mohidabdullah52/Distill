# RAG Document Summarizer — Full Project Specification
> **Cursor Prompt:** Read this entire document before writing a single line of code. Every section is load-bearing. Follow the file structure exactly, use the libraries specified, and implement every feature described. When in doubt, re-read the relevant section.

---

## 0. Project Overview

Build a **RAG-powered document summarization web app** that:

1. Accepts one or more **PDF** and/or **PPTX** files via drag-and-drop or file picker
2. Ingests them into a **local ChromaDB vector store**
3. Uses an **LLM (Ollama / OpenAI-compatible)** to retrieve relevant chunks and synthesize a compact, structured summary
4. Returns a **downloadable PDF** containing only the essential information

**Timeline:** 1–2 days of focused development  
**Team:** Solo developer using Cursor AI

---

## 1. Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Backend framework | FastAPI | `^0.111` |
| Vector DB | ChromaDB | `^0.5` (local, file-persisted) |
| Embeddings | `sentence-transformers` | `^3.0` (local, `all-MiniLM-L6-v2`) |
| LLM | Ollama via `openai` SDK (OpenAI-compatible endpoint) | latest |
| PDF parsing | `pypdf` | `^4.0` |
| PPTX parsing | `python-pptx` | `^0.6` |
| PDF generation | `reportlab` | `^4.0` |
| Frontend framework | React + Vite | `^5.x` |
| UI library | MUI (Material UI) | `^5.x` |
| HTTP client | `axios` | `^1.x` |
| State management | React `useState` / `useReducer` (no external lib) |  |

> **LLM Note:** The backend calls `http://localhost:11434/v1` (Ollama default). If the user has an OpenAI key instead, they set `LLM_BASE_URL=https://api.openai.com/v1` and `LLM_API_KEY=sk-...` in `.env`. The same code works for both.

---

## 2. Repository Structure

```
rag-summarizer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app, CORS, routes
│   │   ├── config.py                # Pydantic settings (env vars)
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── ingest.py            # POST /api/ingest
│   │   │   └── summarize.py         # POST /api/summarize
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── parser.py            # PDF + PPTX text extraction
│   │   │   ├── chunker.py           # Text chunking logic
│   │   │   ├── embedder.py          # ChromaDB + sentence-transformers
│   │   │   ├── retriever.py         # Similarity search wrapper
│   │   │   ├── llm.py               # LLM call via openai SDK
│   │   │   └── pdf_generator.py     # ReportLab PDF builder
│   │   └── models/
│   │       ├── __init__.py
│   │       └── schemas.py           # Pydantic request/response models
│   ├── chroma_db/                   # Auto-created, gitignored
│   ├── uploads/                     # Temp upload storage, gitignored
│   ├── outputs/                     # Generated PDFs, gitignored
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── theme.js                 # MUI theme customization
│   │   ├── components/
│   │   │   ├── DropZone.jsx         # File upload area
│   │   │   ├── FileList.jsx         # Uploaded files chips/list
│   │   │   ├── ProcessingStatus.jsx # Stepper: ingest → summarize → done
│   │   │   ├── ResultCard.jsx       # Download button + summary preview
│   │   │   └── ErrorAlert.jsx       # Snackbar error display
│   │   ├── hooks/
│   │   │   └── useDocumentPipeline.js  # All API calls, state machine
│   │   └── api/
│   │       └── client.js            # axios instance
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── docker-compose.yml               # Optional: wrap everything
└── README.md
```

---

## 3. Backend — Detailed Implementation

### 3.1 `backend/requirements.txt`

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
python-multipart==0.0.9
pypdf==4.2.0
python-pptx==0.6.23
chromadb==0.5.3
sentence-transformers==3.0.1
openai==1.30.0
reportlab==4.2.0
pydantic-settings==2.2.1
python-dotenv==1.0.1
aiofiles==23.2.1
```

---

### 3.2 `backend/.env.example`

```
# Copy to .env and fill in values

# LLM config (Ollama default shown)
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=llama3

# ChromaDB persistence directory
CHROMA_PERSIST_DIR=./chroma_db

# Upload + output temp dirs
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs

# Chunking
CHUNK_SIZE=800
CHUNK_OVERLAP=100

# Retrieval
TOP_K_CHUNKS=12
```

---

### 3.3 `backend/app/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    llm_model: str = "llama3"

    chroma_persist_dir: str = "./chroma_db"
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"

    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k_chunks: int = 12

settings = Settings()
```

---

### 3.4 `backend/app/models/schemas.py`

```python
from pydantic import BaseModel
from typing import List, Optional

class IngestResponse(BaseModel):
    session_id: str
    files_processed: List[str]
    total_chunks: int
    message: str

class SummarizeRequest(BaseModel):
    session_id: str
    focus_prompt: Optional[str] = None   # Optional user hint

class SummarizeResponse(BaseModel):
    session_id: str
    pdf_filename: str
    download_url: str
    summary_preview: str                  # First ~500 chars of summary text
```

---

### 3.5 `backend/app/services/parser.py`

Extract clean text from uploaded files. Return a list of `(source_name, page_or_slide_num, text)` tuples.

```python
import io
from pathlib import Path
from typing import List, Tuple

def extract_text(file_path: Path) -> List[Tuple[str, int, str]]:
    """
    Returns list of (source_label, page_number, text_content).
    source_label = filename
    page_number  = 1-indexed page (PDF) or slide (PPTX)
    """
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(file_path)
    elif suffix in (".pptx", ".ppt"):
        return _extract_pptx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def _extract_pdf(path: Path) -> List[Tuple[str, int, str]]:
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    results = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            results.append((path.name, i, text))
    return results


def _extract_pptx(path: Path) -> List[Tuple[str, int, str]]:
    from pptx import Presentation
    prs = Presentation(str(path))
    results = []
    for i, slide in enumerate(prs.slides, start=1):
        parts = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    line = " ".join(run.text for run in para.runs).strip()
                    if line:
                        parts.append(line)
        text = "\n".join(parts).strip()
        if text:
            results.append((path.name, i, text))
    return results
```

---

### 3.6 `backend/app/services/chunker.py`

Simple sliding-window character chunker. Returns list of dicts ready for ChromaDB insertion.

```python
from typing import List, Dict, Any
from app.config import settings

def chunk_pages(
    pages: list,  # List[Tuple[source, page_num, text]]
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> List[Dict[str, Any]]:
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    chunks = []
    chunk_id = 0

    for source, page_num, text in pages:
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "id": f"{source}__p{page_num}__c{chunk_id}",
                    "text": chunk_text,
                    "metadata": {
                        "source": source,
                        "page": page_num,
                    },
                })
                chunk_id += 1
            start += chunk_size - chunk_overlap

    return chunks
```

---

### 3.7 `backend/app/services/embedder.py`

Wrap ChromaDB. One collection per session so multiple concurrent users don't collide.

```python
import chromadb
from chromadb.utils import embedding_functions
from app.config import settings
from typing import List, Dict, Any

# Module-level client (reused across requests)
_client: chromadb.ClientAPI = None

def _get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return _client


def _get_ef():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )


def upsert_chunks(session_id: str, chunks: List[Dict[str, Any]]) -> int:
    """Insert chunks into a session-scoped ChromaDB collection."""
    client = _get_client()
    ef = _get_ef()
    # ChromaDB collection names must be alphanumeric + hyphens
    collection_name = f"session-{session_id.replace('_', '-')}"
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
    )
    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )
    return len(chunks)


def query_chunks(session_id: str, query_text: str, top_k: int = None) -> List[str]:
    """Return top-k most relevant chunk texts for a query."""
    top_k = top_k or settings.top_k_chunks
    client = _get_client()
    ef = _get_ef()
    collection_name = f"session-{session_id.replace('_', '-')}"
    collection = client.get_collection(name=collection_name, embedding_function=ef)
    results = collection.query(
        query_texts=[query_text],
        n_results=top_k,
    )
    return results["documents"][0]  # flat list of strings


def delete_session(session_id: str):
    """Cleanup: delete collection when no longer needed."""
    try:
        client = _get_client()
        collection_name = f"session-{session_id.replace('_', '-')}"
        client.delete_collection(collection_name)
    except Exception:
        pass  # Best-effort cleanup
```

---

### 3.8 `backend/app/services/llm.py`

Single function: given retrieved chunks + optional user focus, return structured summary text.

```python
from openai import OpenAI
from app.config import settings
from typing import List

_client: OpenAI = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
        )
    return _client


SYSTEM_PROMPT = """You are an expert document analyst and technical writer.
Your task is to synthesize retrieved document chunks into a single, compact, well-structured summary.

Output format (use exactly these Markdown headings):
## Executive Summary
(2-4 sentences covering the main thesis / purpose)

## Key Findings & Insights
(bullet list, max 10 bullets, each 1-2 sentences)

## Important Details & Data
(any critical numbers, dates, names, statistics, formulas)

## Action Items / Recommendations
(if any exist in the source material; otherwise omit this section)

## Glossary
(define any domain-specific terms found; 3-8 entries; omit if not applicable)

Rules:
- Be concise. Cut filler. Every word must earn its place.
- Preserve factual accuracy. Do not hallucinate.
- If information repeats across chunks, consolidate — do not duplicate.
- Do not reference "the document" or "the chunks"; write as if authoring a summary report.
"""


def generate_summary(chunks: List[str], focus_prompt: str = None) -> str:
    client = _get_client()

    context = "\n\n---\n\n".join(chunks)

    user_content = f"Here are the relevant document excerpts:\n\n{context}"
    if focus_prompt:
        user_content += f"\n\nUser focus area: {focus_prompt}"
    user_content += "\n\nGenerate the structured summary now."

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()
```

---

### 3.9 `backend/app/services/pdf_generator.py`

Convert the Markdown-structured summary text into a clean, professional PDF using ReportLab.

```python
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import re


ACCENT_COLOR = colors.HexColor("#1565C0")   # MUI primary blue
LIGHT_GRAY   = colors.HexColor("#F5F5F5")
DARK_GRAY    = colors.HexColor("#424242")


def _build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="DocTitle",
        fontSize=22, leading=28, textColor=ACCENT_COLOR,
        spaceAfter=6, alignment=TA_CENTER, fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="DocSubtitle",
        fontSize=10, leading=14, textColor=DARK_GRAY,
        spaceAfter=20, alignment=TA_CENTER, fontName="Helvetica"
    ))
    styles.add(ParagraphStyle(
        name="H2",
        fontSize=13, leading=18, textColor=ACCENT_COLOR,
        spaceBefore=16, spaceAfter=6, fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="Body",
        fontSize=10, leading=15, textColor=DARK_GRAY,
        spaceAfter=6, fontName="Helvetica"
    ))
    styles.add(ParagraphStyle(
        name="BulletText",
        fontSize=10, leading=15, textColor=DARK_GRAY,
        fontName="Helvetica", leftIndent=10
    ))
    return styles


def markdown_to_pdf(summary_text: str, output_path: Path, source_files: list[str]):
    """Convert LLM markdown summary to a polished ReportLab PDF."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    styles = _build_styles()
    story = []

    # Title block
    story.append(Paragraph("Document Summary Report", styles["DocTitle"]))
    sources_label = ", ".join(source_files) if source_files else "Multiple Files"
    ts = datetime.now().strftime("%B %d, %Y %H:%M")
    story.append(Paragraph(f"Sources: {sources_label} &nbsp;|&nbsp; Generated: {ts}", styles["DocSubtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_COLOR, spaceAfter=12))

    # Parse markdown sections
    lines = summary_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if line.startswith("## "):
            heading = line[3:].strip()
            story.append(Paragraph(heading, styles["H2"]))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=4))

        elif line.startswith("- ") or line.startswith("* "):
            # Collect consecutive bullet lines
            bullets = []
            while i < len(lines) and (lines[i].startswith("- ") or lines[i].startswith("* ")):
                bullet_text = lines[i][2:].strip()
                bullets.append(ListItem(Paragraph(bullet_text, styles["BulletText"]), bulletColor=ACCENT_COLOR))
                i += 1
            story.append(ListFlowable(bullets, bulletType="bullet", start="•", leftIndent=20))
            continue

        elif line.strip() == "":
            story.append(Spacer(1, 6))

        else:
            # Plain body text
            # Convert inline bold **text** → <b>text</b>
            line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
            story.append(Paragraph(line, styles["Body"]))

        i += 1

    doc.build(story)
```

---

### 3.10 `backend/app/routes/ingest.py`

```python
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.config import settings
from app.models.schemas import IngestResponse
from app.services.parser import extract_text
from app.services.chunker import chunk_pages
from app.services.embedder import upsert_chunks

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".pptx", ".ppt"}


@router.post("/ingest", response_model=IngestResponse)
async def ingest_files(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    session_id = str(uuid.uuid4()).replace("-", "")[:16]
    upload_dir = Path(settings.upload_dir) / session_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    files_processed = []
    all_chunks = []

    for upload in files:
        suffix = Path(upload.filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{suffix}'. Allowed: PDF, PPTX"
            )

        dest = upload_dir / upload.filename
        with open(dest, "wb") as f:
            shutil.copyfileobj(upload.file, f)

        try:
            pages = extract_text(dest)
            chunks = chunk_pages(pages)
            all_chunks.extend(chunks)
            files_processed.append(upload.filename)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Failed to parse {upload.filename}: {e}")

    if not all_chunks:
        raise HTTPException(status_code=422, detail="No text could be extracted from the uploaded files.")

    total = upsert_chunks(session_id, all_chunks)

    return IngestResponse(
        session_id=session_id,
        files_processed=files_processed,
        total_chunks=total,
        message=f"Ingested {len(files_processed)} file(s) → {total} chunks indexed."
    )
```

---

### 3.11 `backend/app/routes/summarize.py`

```python
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.config import settings
from app.models.schemas import SummarizeRequest, SummarizeResponse
from app.services.retriever import retrieve_for_summary
from app.services.llm import generate_summary
from app.services.pdf_generator import markdown_to_pdf
from app.services.embedder import query_chunks

router = APIRouter()

# Broad queries to pull comprehensive content from the vector store
RETRIEVAL_QUERIES = [
    "main topic purpose objective",
    "key findings results conclusions",
    "important data statistics numbers dates",
    "recommendations action items next steps",
    "definitions concepts terminology",
]


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest):
    session_id = req.session_id

    # Retrieve relevant chunks using multiple query angles
    seen = set()
    retrieved_chunks = []
    per_query_k = max(3, settings.top_k_chunks // len(RETRIEVAL_QUERIES))

    for q in RETRIEVAL_QUERIES:
        try:
            chunks = query_chunks(session_id, q, top_k=per_query_k)
            for chunk in chunks:
                if chunk not in seen:
                    seen.add(chunk)
                    retrieved_chunks.append(chunk)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Session not found or ChromaDB error: {e}")

    if not retrieved_chunks:
        raise HTTPException(status_code=404, detail="No chunks found for this session. Please re-upload files.")

    # Generate summary via LLM
    summary_text = generate_summary(retrieved_chunks, focus_prompt=req.focus_prompt)

    # Generate PDF
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_filename = f"summary_{session_id}.pdf"
    pdf_path = output_dir / pdf_filename

    # Derive source file names from chunk metadata if available (best-effort)
    source_files = []  # We'll pull them from the summary context
    markdown_to_pdf(summary_text, pdf_path, source_files)

    summary_preview = summary_text[:500] + ("..." if len(summary_text) > 500 else "")

    return SummarizeResponse(
        session_id=session_id,
        pdf_filename=pdf_filename,
        download_url=f"/api/download/{pdf_filename}",
        summary_preview=summary_preview,
    )


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    output_dir = Path(settings.output_dir)
    file_path = output_dir / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    # Security: ensure path doesn't escape outputs dir
    if not str(file_path.resolve()).startswith(str(output_dir.resolve())):
        raise HTTPException(status_code=403, detail="Forbidden")
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename,
    )
```

---

### 3.12 `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.ingest import router as ingest_router
from app.routes.summarize import router as summarize_router
from pathlib import Path
from app.config import settings

app = FastAPI(
    title="RAG Document Summarizer",
    version="1.0.0",
    description="Ingest PDFs and PPTXs, get a concise summary PDF back."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure dirs exist at startup
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.output_dir).mkdir(parents=True, exist_ok=True)

app.include_router(ingest_router, prefix="/api")
app.include_router(summarize_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
```

---

## 4. Frontend — Detailed Implementation

### 4.1 `frontend/package.json`

```json
{
  "name": "rag-summarizer-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "@mui/icons-material": "^5.15.0",
    "@mui/material": "^5.15.0",
    "axios": "^1.7.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "vite": "^5.3.0"
  }
}
```

---

### 4.2 `frontend/vite.config.js`

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

---

### 4.3 `frontend/src/theme.js`

```js
import { createTheme } from '@mui/material/styles'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1565C0',
      light: '#E3F2FD',
      dark: '#0D47A1',
    },
    secondary: {
      main: '#00897B',
    },
    background: {
      default: '#F8FAFD',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#1A1A2E',
      secondary: '#5C6B7A',
    },
  },
  typography: {
    fontFamily: '"DM Sans", "Helvetica Neue", Arial, sans-serif',
    h4: { fontWeight: 700, letterSpacing: '-0.5px' },
    h6: { fontWeight: 600 },
    body2: { lineHeight: 1.7 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 8,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 6 },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none' },
      },
    },
  },
})

export default theme
```

> **Note to Cursor:** Import the `DM Sans` Google Font in `index.html`:
> ```html
> <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
> ```

---

### 4.4 `frontend/src/api/client.js`

```js
import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 120000, // 2 min — LLM can be slow
})

export default client
```

---

### 4.5 `frontend/src/hooks/useDocumentPipeline.js`

This hook is the core state machine. It manages all async flow: idle → uploading → ingesting → summarizing → done (or error).

```js
import { useReducer, useCallback } from 'react'
import client from '../api/client'

const STEPS = ['Upload Files', 'Index Documents', 'Generate Summary', 'Download PDF']

const initialState = {
  status: 'idle',       // idle | uploading | ingesting | summarizing | done | error
  activeStep: 0,
  files: [],            // File objects chosen by user
  sessionId: null,
  filesProcessed: [],
  totalChunks: 0,
  downloadUrl: null,
  pdfFilename: null,
  summaryPreview: null,
  error: null,
}

function reducer(state, action) {
  switch (action.type) {
    case 'SET_FILES':
      return { ...state, files: action.payload, error: null }
    case 'START_UPLOAD':
      return { ...state, status: 'uploading', activeStep: 0, error: null }
    case 'INGEST_SUCCESS':
      return {
        ...state, status: 'ingesting', activeStep: 1,
        sessionId: action.payload.session_id,
        filesProcessed: action.payload.files_processed,
        totalChunks: action.payload.total_chunks,
      }
    case 'START_SUMMARIZE':
      return { ...state, status: 'summarizing', activeStep: 2 }
    case 'SUMMARIZE_SUCCESS':
      return {
        ...state, status: 'done', activeStep: 3,
        downloadUrl: action.payload.download_url,
        pdfFilename: action.payload.pdf_filename,
        summaryPreview: action.payload.summary_preview,
      }
    case 'ERROR':
      return { ...state, status: 'error', error: action.payload }
    case 'RESET':
      return { ...initialState }
    default:
      return state
  }
}

export function useDocumentPipeline() {
  const [state, dispatch] = useReducer(reducer, initialState)

  const addFiles = useCallback((newFiles) => {
    dispatch({
      type: 'SET_FILES',
      payload: [...state.files, ...Array.from(newFiles)].slice(0, 10) // max 10 files
    })
  }, [state.files])

  const removeFile = useCallback((index) => {
    dispatch({
      type: 'SET_FILES',
      payload: state.files.filter((_, i) => i !== index)
    })
  }, [state.files])

  const run = useCallback(async (focusPrompt = '') => {
    if (state.files.length === 0) return

    dispatch({ type: 'START_UPLOAD' })

    // Step 1: Ingest
    const formData = new FormData()
    state.files.forEach(f => formData.append('files', f))

    let ingestData
    try {
      const res = await client.post('/ingest', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      ingestData = res.data
      dispatch({ type: 'INGEST_SUCCESS', payload: ingestData })
    } catch (err) {
      dispatch({ type: 'ERROR', payload: err.response?.data?.detail || 'Failed to ingest files.' })
      return
    }

    // Step 2: Summarize
    dispatch({ type: 'START_SUMMARIZE' })
    try {
      const res = await client.post('/summarize', {
        session_id: ingestData.session_id,
        focus_prompt: focusPrompt || null,
      })
      dispatch({ type: 'SUMMARIZE_SUCCESS', payload: res.data })
    } catch (err) {
      dispatch({ type: 'ERROR', payload: err.response?.data?.detail || 'Failed to generate summary.' })
    }
  }, [state.files])

  const reset = useCallback(() => dispatch({ type: 'RESET' }), [])

  return { state, STEPS, addFiles, removeFile, run, reset }
}
```

---

### 4.6 `frontend/src/components/DropZone.jsx`

Accepts PDF and PPTX files. Supports both drag-and-drop and click-to-browse.

```jsx
import { useRef, useState } from 'react'
import { Box, Typography, Button } from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'

const ACCEPTED = '.pdf,.pptx,.ppt'

export default function DropZone({ onFilesAdded, disabled }) {
  const inputRef = useRef()
  const [dragging, setDragging] = useState(false)

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    if (disabled) return
    const files = Array.from(e.dataTransfer.files).filter(f =>
      /\.(pdf|pptx|ppt)$/i.test(f.name)
    )
    if (files.length) onFilesAdded(files)
  }

  return (
    <Box
      onDragEnter={() => !disabled && setDragging(true)}
      onDragLeave={() => setDragging(false)}
      onDragOver={e => e.preventDefault()}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      sx={{
        border: '2px dashed',
        borderColor: dragging ? 'primary.main' : 'grey.300',
        borderRadius: 3,
        py: 6,
        px: 4,
        textAlign: 'center',
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'all 0.2s ease',
        bgcolor: dragging ? 'primary.light' : 'background.paper',
        opacity: disabled ? 0.5 : 1,
        '&:hover': !disabled ? { borderColor: 'primary.main', bgcolor: 'primary.light' } : {},
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        multiple
        hidden
        onChange={e => onFilesAdded(Array.from(e.target.files))}
      />
      <CloudUploadIcon sx={{ fontSize: 52, color: 'primary.main', mb: 1 }} />
      <Typography variant="h6" gutterBottom>
        Drag & drop files here
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={2}>
        Supports PDF and PPTX — up to 10 files
      </Typography>
      <Button variant="outlined" size="small" disabled={disabled}>
        Browse Files
      </Button>
    </Box>
  )
}
```

---

### 4.7 `frontend/src/components/FileList.jsx`

```jsx
import { Box, Chip, Typography } from '@mui/material'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import SlideshowIcon from '@mui/icons-material/Slideshow'

function getIcon(name) {
  return /\.pdf$/i.test(name) ? <PictureAsPdfIcon fontSize="small" /> : <SlideshowIcon fontSize="small" />
}

export default function FileList({ files, onRemove, disabled }) {
  if (!files.length) return null
  return (
    <Box mt={2}>
      <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: 'block' }}>
        {files.length} file{files.length > 1 ? 's' : ''} selected
      </Typography>
      <Box display="flex" flexWrap="wrap" gap={1}>
        {files.map((f, i) => (
          <Chip
            key={i}
            icon={getIcon(f.name)}
            label={f.name}
            onDelete={disabled ? undefined : () => onRemove(i)}
            color="primary"
            variant="outlined"
            size="small"
          />
        ))}
      </Box>
    </Box>
  )
}
```

---

### 4.8 `frontend/src/components/ProcessingStatus.jsx`

```jsx
import { Box, Stepper, Step, StepLabel, LinearProgress, Typography } from '@mui/material'

const STATUS_LABELS = {
  uploading: 'Uploading files...',
  ingesting: 'Indexing into vector store...',
  summarizing: 'Generating summary with AI...',
  done: 'Complete!',
}

export default function ProcessingStatus({ activeStep, steps, status, totalChunks }) {
  const isActive = ['uploading', 'ingesting', 'summarizing'].includes(status)

  return (
    <Box mt={4}>
      <Stepper activeStep={activeStep} alternativeLabel>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {isActive && (
        <Box mt={3}>
          <LinearProgress color="primary" />
          <Typography variant="body2" color="text.secondary" textAlign="center" mt={1}>
            {STATUS_LABELS[status]}
            {status === 'ingesting' && totalChunks > 0 && ` (${totalChunks} chunks indexed)`}
          </Typography>
        </Box>
      )}
    </Box>
  )
}
```

---

### 4.9 `frontend/src/components/ResultCard.jsx`

```jsx
import { Box, Paper, Typography, Button, Divider } from '@mui/material'
import DownloadIcon from '@mui/icons-material/Download'
import RestartAltIcon from '@mui/icons-material/RestartAlt'

export default function ResultCard({ downloadUrl, pdfFilename, summaryPreview, onReset }) {
  return (
    <Paper elevation={2} sx={{ mt: 4, p: 3, borderRadius: 3, border: '1px solid', borderColor: 'success.light' }}>
      <Typography variant="h6" color="success.dark" gutterBottom>
        ✅ Summary Ready
      </Typography>

      {summaryPreview && (
        <>
          <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>
            Preview
          </Typography>
          <Box
            sx={{
              bgcolor: 'grey.50',
              borderRadius: 2,
              p: 2,
              maxHeight: 160,
              overflow: 'hidden',
              position: 'relative',
              '&::after': {
                content: '""',
                position: 'absolute',
                bottom: 0, left: 0, right: 0,
                height: 40,
                background: 'linear-gradient(transparent, #F8F9FA)',
              }
            }}
          >
            <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
              {summaryPreview}
            </Typography>
          </Box>
          <Divider sx={{ my: 2 }} />
        </>
      )}

      <Box display="flex" gap={2} flexWrap="wrap">
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          href={downloadUrl}
          download={pdfFilename}
          target="_blank"
          rel="noopener noreferrer"
        >
          Download PDF
        </Button>
        <Button
          variant="outlined"
          startIcon={<RestartAltIcon />}
          onClick={onReset}
        >
          Start Over
        </Button>
      </Box>
    </Paper>
  )
}
```

---

### 4.10 `frontend/src/components/ErrorAlert.jsx`

```jsx
import { Alert, AlertTitle, Button, Box } from '@mui/material'

export default function ErrorAlert({ message, onDismiss }) {
  if (!message) return null
  return (
    <Box mt={3}>
      <Alert severity="error" action={
        <Button color="inherit" size="small" onClick={onDismiss}>Dismiss</Button>
      }>
        <AlertTitle>Error</AlertTitle>
        {message}
      </Alert>
    </Box>
  )
}
```

---

### 4.11 `frontend/src/App.jsx`

```jsx
import { useState } from 'react'
import {
  ThemeProvider, CssBaseline,
  Container, Box, Typography, Paper,
  TextField, Button, Divider
} from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import theme from './theme'
import DropZone from './components/DropZone'
import FileList from './components/FileList'
import ProcessingStatus from './components/ProcessingStatus'
import ResultCard from './components/ResultCard'
import ErrorAlert from './components/ErrorAlert'
import { useDocumentPipeline } from './hooks/useDocumentPipeline'

export default function App() {
  const { state, STEPS, addFiles, removeFile, run, reset } = useDocumentPipeline()
  const [focusPrompt, setFocusPrompt] = useState('')

  const isProcessing = ['uploading', 'ingesting', 'summarizing'].includes(state.status)
  const isDone = state.status === 'done'

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        minHeight="100vh"
        bgcolor="background.default"
        display="flex"
        alignItems="flex-start"
        justifyContent="center"
        pt={6}
        pb={8}
      >
        <Container maxWidth="sm">
          {/* Header */}
          <Box textAlign="center" mb={4}>
            <Box display="flex" alignItems="center" justifyContent="center" gap={1} mb={1}>
              <AutoAwesomeIcon color="primary" sx={{ fontSize: 32 }} />
              <Typography variant="h4" color="primary.dark">
                Doc Summarizer
              </Typography>
            </Box>
            <Typography variant="body1" color="text.secondary">
              Upload PDFs or PowerPoints — get a compact, AI-generated summary PDF
            </Typography>
          </Box>

          {/* Main Card */}
          <Paper elevation={1} sx={{ p: 4, borderRadius: 3 }}>
            <DropZone onFilesAdded={addFiles} disabled={isProcessing || isDone} />
            <FileList files={state.files} onRemove={removeFile} disabled={isProcessing} />

            {state.files.length > 0 && !isDone && (
              <>
                <Divider sx={{ my: 3 }} />
                <TextField
                  fullWidth
                  label="Focus area (optional)"
                  placeholder="e.g. financial projections, technical architecture, risks..."
                  value={focusPrompt}
                  onChange={e => setFocusPrompt(e.target.value)}
                  disabled={isProcessing}
                  size="small"
                  helperText="Guide the AI to emphasize specific topics"
                  sx={{ mb: 2 }}
                />
                <Button
                  variant="contained"
                  fullWidth
                  size="large"
                  onClick={() => run(focusPrompt)}
                  disabled={isProcessing || state.files.length === 0}
                >
                  {isProcessing ? 'Processing…' : 'Generate Summary PDF'}
                </Button>
              </>
            )}

            {/* Processing Steps */}
            {(isProcessing || isDone) && (
              <ProcessingStatus
                activeStep={state.activeStep}
                steps={STEPS}
                status={state.status}
                totalChunks={state.totalChunks}
              />
            )}

            {/* Error */}
            <ErrorAlert
              message={state.error}
              onDismiss={reset}
            />
          </Paper>

          {/* Result */}
          {isDone && (
            <ResultCard
              downloadUrl={state.downloadUrl}
              pdfFilename={state.pdfFilename}
              summaryPreview={state.summaryPreview}
              onReset={reset}
            />
          )}
        </Container>
      </Box>
    </ThemeProvider>
  )
}
```

---

### 4.12 `frontend/src/main.jsx`

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

---

### 4.13 `frontend/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Doc Summarizer</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
```

---

## 5. API Contract Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/ingest` | Upload files (multipart), returns `session_id` |
| `POST` | `/api/summarize` | Takes `session_id`, returns download URL |
| `GET` | `/api/download/{filename}` | Download generated PDF |

### POST `/api/ingest` — Request
`Content-Type: multipart/form-data`  
Field: `files` (one or more files)

### POST `/api/ingest` — Response `200`
```json
{
  "session_id": "abc123def456",
  "files_processed": ["report.pdf", "slides.pptx"],
  "total_chunks": 84,
  "message": "Ingested 2 file(s) → 84 chunks indexed."
}
```

### POST `/api/summarize` — Request
```json
{
  "session_id": "abc123def456",
  "focus_prompt": "focus on financial data"
}
```

### POST `/api/summarize` — Response `200`
```json
{
  "session_id": "abc123def456",
  "pdf_filename": "summary_abc123def456.pdf",
  "download_url": "/api/download/summary_abc123def456.pdf",
  "summary_preview": "## Executive Summary\n\nThis document outlines..."
}
```

---

## 6. Local Setup Guide

### Prerequisites
- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.ai) installed and running, with at least one model pulled:
  ```bash
  ollama pull llama3
  ollama serve  # runs on :11434
  ```
  *(Or set `LLM_BASE_URL` + `LLM_API_KEY` in `.env` for OpenAI)*

### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env if needed (especially LLM_MODEL)

uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Opens on http://localhost:5173
```

### First Run
1. Open `http://localhost:5173`
2. Drag in 1–3 PDFs or PPTX files
3. Optionally enter a focus area
4. Click **Generate Summary PDF**
5. Wait ~30–90 seconds (embedding + LLM)
6. Download the generated PDF

---

## 7. Data Flow Diagram

```
User Browser
    │
    │ 1. multipart/form-data (files)
    ▼
FastAPI /api/ingest
    │
    ├── parser.py: extract text from PDF / PPTX
    │     → list of (source, page, text)
    │
    ├── chunker.py: sliding-window chunking
    │     → list of {id, text, metadata}
    │
    └── embedder.py: sentence-transformers → ChromaDB upsert
          → session-scoped collection (persisted to disk)

    │ 2. POST /api/summarize {session_id}
    ▼
FastAPI /api/summarize
    │
    ├── embedder.query_chunks (5 query angles × top_k)
    │     → deduplicated relevant chunks
    │
    ├── llm.generate_summary → Ollama / OpenAI
    │     → structured markdown text
    │
    └── pdf_generator.markdown_to_pdf → ReportLab → .pdf file

    │ 3. GET /api/download/{filename}
    ▼
User Browser → FileResponse (PDF download)
```

---

## 8. Key Design Decisions

| Decision | Rationale |
|---|---|
| **ChromaDB local file persistence** | Zero infrastructure — no Docker or external service needed. Data persists between restarts. |
| **Session-scoped collections** | Isolates concurrent users; cheap to create/delete in ChromaDB. |
| **`all-MiniLM-L6-v2` embeddings** | Fast, local, 80MB model. Good quality for English. Runs on CPU. |
| **Multi-query retrieval (5 angles)** | Single generic query misses domain-specific content. 5 semantic angles cast a wider net. |
| **ReportLab for PDF output** | Pure Python, no headless Chrome, no external tools. Simple and deterministic. |
| **Vite proxy → backend** | Avoids CORS complexity in dev. In production, put nginx in front. |
| **No auth / no DB** | Maximizes build speed. Sessions are UUID-keyed; files are temp. Add auth/DB in v2 if needed. |

---

## 9. Error Handling Rules

### Backend
- All route handlers wrap service calls in `try/except` and raise `HTTPException` with meaningful `detail` strings
- Parser errors per-file → 422 with filename in message
- ChromaDB collection not found → 404 (session expired or wrong ID)
- LLM timeout → propagates as 500 (let OpenAI SDK raise)

### Frontend
- All errors land in `state.error` via the `ERROR` dispatch
- `ErrorAlert` renders it below the main card with a Dismiss button that calls `reset()`
- axios timeout set to 120s (LLM can be slow on CPU)

---

## 10. File Size & Edge Case Handling

| Scenario | Handling |
|---|---|
| Empty pages / blank slides | `parser.py` skips pages with no text after `.strip()` |
| Very large files (>100MB) | Add `MAX_FILE_SIZE = 50 * 1024 * 1024` check in ingest route; return 413 |
| Scanned PDF (no text layer) | `pypdf` returns empty string → skip + warn in response message |
| 0 chunks after parsing | Ingest returns 422: "No text could be extracted" |
| Session ID not found in summarize | Raises 404 with helpful message |
| Duplicate file uploads | `upsert` in ChromaDB is idempotent — safe to re-upload |

---

## 11. Production Considerations (Future / Optional)

These are **not required for the 2-day build** but note them for later:

- **Cleanup job:** Periodically delete `uploads/`, `outputs/`, and ChromaDB collections older than 24h
- **Rate limiting:** Add `slowapi` middleware if exposed publicly
- **Auth:** JWT via `fastapi-users` if multi-tenant
- **Async embeddings:** Move ChromaDB upsert to a background task (`BackgroundTasks`) for large files
- **nginx:** Put in front for SSL, static file serving, and load balancing
- **Docker Compose:** See section 12

---

## 12. Optional `docker-compose.yml`

```yaml
version: "3.9"
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend/chroma_db:/app/chroma_db
      - ./backend/uploads:/app/uploads
      - ./backend/outputs:/app/outputs
    env_file:
      - ./backend/.env

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:80"
    depends_on:
      - backend
```

> **Dockerfile for backend (`backend/Dockerfile`):**
> ```dockerfile
> FROM python:3.11-slim
> WORKDIR /app
> COPY requirements.txt .
> RUN pip install --no-cache-dir -r requirements.txt
> COPY . .
> CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
> ```

> **Dockerfile for frontend (`frontend/Dockerfile`):**
> ```dockerfile
> FROM node:20-alpine AS build
> WORKDIR /app
> COPY package*.json ./
> RUN npm install
> COPY . .
> RUN npm run build
>
> FROM nginx:alpine
> COPY --from=build /app/dist /usr/share/nginx/html
> COPY nginx.conf /etc/nginx/conf.d/default.conf
> ```

---

## 13. Build Order for Cursor

Follow this exact order to avoid import errors:

1. `backend/requirements.txt` and `.env.example`
2. `backend/app/config.py`
3. `backend/app/models/schemas.py`
4. `backend/app/services/parser.py`
5. `backend/app/services/chunker.py`
6. `backend/app/services/embedder.py`
7. `backend/app/services/llm.py`
8. `backend/app/services/pdf_generator.py`
9. `backend/app/routes/ingest.py`
10. `backend/app/routes/summarize.py`
11. `backend/app/main.py`
12. `frontend/package.json` + `vite.config.js`
13. `frontend/index.html`
14. `frontend/src/theme.js`
15. `frontend/src/api/client.js`
16. `frontend/src/hooks/useDocumentPipeline.js`
17. `frontend/src/components/` (all 5 components)
18. `frontend/src/App.jsx`
19. `frontend/src/main.jsx`
20. `README.md`

---

## 14. README.md (to create)

```markdown
# RAG Document Summarizer

Upload PDFs and PowerPoint files → get a compact AI-generated summary PDF.

## Stack
- **Backend:** FastAPI + ChromaDB + sentence-transformers + Ollama
- **Frontend:** React + Vite + MUI

## Quick Start

### 1. Install Ollama and pull a model
```
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3
```

### 2. Start backend
```
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### 3. Start frontend
```
cd frontend
npm install && npm run dev
```

### 4. Open http://localhost:5173
```

---

*Document version: 1.0 — Last updated: June 2026*
