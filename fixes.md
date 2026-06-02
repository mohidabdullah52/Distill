# Project Fixes, Optimizations, and Improvements

This document lists potential bugs, resource leaks, security risks, performance bottlenecks, and user experience issues identified in the codebase.

---

## 🔴 Priority P0: Bugs & Security Issues

### 1. Download Button URL Fragility
- **Component**: Frontend Result Card / Download Flow
- **Files**:
  - [ResultCard.tsx](file:///d:/Projects/Summarag/frontend/src/components/ResultCard.tsx#L82) (`href={downloadUrl || '#'}`)
  - [summarize.py](file:///d:/Projects/Summarag/backend/app/routes/summarize.py#L74) (`download_url=f"/api/download/{pdf_filename}"`)
- **Problem**: The backend returns `download_url` as `/api/download/{filename}`. The `<a>` tag in `ResultCard.tsx` uses this URL directly as the `href`. While this works through the Vite dev proxy (port 5173), if the backend URL ever changes or a different base path is used, the hard-coded `/api/` prefix in the backend response becomes fragile.
- **Consequence**: Tight coupling between backend URL prefix knowledge and frontend rendering. Currently functional but fragile.
- **Remedy**: Use the axios `client` instance (which already has `baseURL: '/api'`) to construct the download URL dynamically on the frontend.

---

## 🟡 Priority P1: Optimizations & Enhancements

### 2. No Session Cleanup After Failed Summarization
- **Component**: Frontend Pipeline Hook
- **Files**:
  - [useDocumentPipeline.ts](file:///d:/Projects/Summarag/frontend/src/hooks/useDocumentPipeline.ts#L187-L193) (error handler in summarize)
- **Problem**: When summarization fails (the second `try/catch` block), the pipeline dispatches an `ERROR` action but never calls the `/cleanup/{session_id}` endpoint. The uploaded files and ChromaDB collections from the successful ingest remain on disk.
- **Consequence**: Every failed summarization attempt leaks a full session (uploaded files + vector collections) until the next server restart triggers lifespan cleanup.
- **Remedy**: Call `client.post('/cleanup/${ingestData.session_id}')` inside the summarize `catch` block, similar to what `reset` and `dismissError` already do.

### 3. Browse Button Does Not Trigger File Selection
- **Component**: Frontend Upload Drop Zone
- **Files**:
  - [DropZone.tsx](file:///d:/Projects/Summarag/frontend/src/components/DropZone.tsx#L110) (`onClick={(e) => e.stopPropagation()}`)
- **Problem**: The "Browse files" button calls `e.stopPropagation()` to prevent the parent `Box`'s click handler from firing twice, but it never triggers `inputRef.current?.click()` itself.
- **Consequence**: Clicking the "Browse files" button does nothing. Users can only select files by clicking the surrounding drop zone area (not the button itself) or by drag-and-drop.
- **Remedy**: Change the button's `onClick` to `(e) => { e.stopPropagation(); inputRef.current?.click(); }`, or remove `stopPropagation()` since the parent already calls `inputRef.current?.click()`.

### 4. Synchronous File Parsing Blocks the Async Event Loop
- **Component**: Backend Ingest Route
- **Files**:
  - [ingest.py](file:///d:/Projects/Summarag/backend/app/routes/ingest.py#L72-L75) (`pages = extract_text(dest)` and `chunks = chunk_pages(pages)`)
- **Problem**: `extract_text` and `chunk_pages` are CPU-bound synchronous functions called directly inside the `async def ingest_files` handler.
- **Consequence**: While parsing large PDF/PPTX files, the entire FastAPI event loop is blocked, causing all concurrent requests (health checks, other uploads, downloads) to stall until parsing finishes.
- **Remedy**: Run the CPU-bound work in a thread pool using `await asyncio.to_thread(extract_text, dest)` and `await asyncio.to_thread(chunk_pages, pages)`.

### 5. LLM Call Has No Timeout or Retry Logic
- **Component**: Backend LLM Service
- **Files**:
  - [llm.py](file:///d:/Projects/Summarag/backend/app/services/llm.py#L112-L119) (`client.chat.completions.create(...)`)
- **Problem**: The OpenAI client call has no explicit `timeout` parameter set. Large documents with many chunks may cause the LLM request to hang indefinitely.
- **Consequence**: If the LLM provider is slow or unresponsive, the summarize endpoint hangs forever, and the frontend shows the "Synthesizing" spinner indefinitely with no feedback.
- **Remedy**: Pass `timeout=120` (or a configurable value from `config.py`) to the `OpenAI()` constructor, and optionally wrap the call in a retry with backoff for transient failures.

---

## 🟢 Priority P2: Small Improvements

### 6. Context Size May Exceed LLM Token Limits
- **Component**: Backend LLM Service
- **Files**:
  - [llm.py](file:///d:/Projects/Summarag/backend/app/services/llm.py#L106-L110) (context concatenation)
  - [retriever.py](file:///d:/Projects/Summarag/backend/app/services/retriever.py#L34) (`per_query_k` calculation)
- **Problem**: All retrieved chunks are concatenated with separators and sent as a single user message. With `top_k_chunks=12` and `chunk_size=800`, plus 5–6 queries each returning ~3 chunks, the concatenated context can reach 15,000+ characters. There is no guard against exceeding the model's context window.
- **Consequence**: If many unique chunks are retrieved, the request may silently truncate input or fail with a token limit error from the LLM provider.
- **Remedy**: Add a character/token budget (configurable in `config.py`) and truncate or prioritize chunks before sending to the model.

### 7. `pdfFilename` Prop Is Unused in ResultCard
- **Component**: Frontend Result Card Component
- **Files**:
  - [ResultCard.tsx](file:///d:/Projects/Summarag/frontend/src/components/ResultCard.tsx#L22-L26) (destructured props omit `pdfFilename`)
- **Problem**: `pdfFilename` is declared in the `ResultCardProps` interface and passed by the parent, but it is destructured away (not included in the function parameter destructuring) and never used in the component.
- **Consequence**: Dead code / unused prop. Minor but indicates the download filename could be shown in the UI for clarity.
- **Remedy**: Use `pdfFilename` in the component to construct the download URL and to display the filename in the success header message.
