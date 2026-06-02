"""
Defines the FastAPI application, middleware, routes, and health endpoint.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.ingest import router as ingest_router
from app.routes.summarize import router as summarize_router
from app.services.llm import get_active_llm_info


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Creates required storage directories when the server starts and cleans up dead sessions.

    Args:
        _app (FastAPI): The running application instance.

    Yields:
        None: Control returns to FastAPI after startup work completes.
    """
    settings.upload_path().mkdir(parents=True, exist_ok=True)
    settings.output_path().mkdir(parents=True, exist_ok=True)
    settings.chroma_path().mkdir(parents=True, exist_ok=True)

    # Clean up leftover files from previous server runs
    import shutil
    for path in [settings.upload_path(), settings.output_path()]:
        if path.exists():
            for item in path.iterdir():
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                except Exception:
                    pass

    # Purge leftover session collections in ChromaDB
    try:
        from app.services.embedder import _get_client
        client = _get_client()
        for col in client.list_collections():
            if col.name.startswith("session-"):
                client.delete_collection(col.name)
    except Exception:
        pass

    yield


app = FastAPI(
    title="RAG Document Summarizer",
    version="1.0.0",
    description="Ingest PDFs and PPTXs, get a concise summary PDF back.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router, prefix="/api")
app.include_router(summarize_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    """
    Reports service health and which LLM provider is configured.

    Returns:
        dict[str, str]: Status plus provider and model when configuration is valid.
    """
    payload: dict[str, str] = {"status": "ok"}
    try:
        payload.update(get_active_llm_info())
    except ValueError as exc:
        payload["llm_config_error"] = str(exc)
    return payload
