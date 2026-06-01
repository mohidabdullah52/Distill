from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.chroma_store import get_chroma_client, get_collection


@asynccontextmanager
async def lifespan(_app: FastAPI):
    get_chroma_client()
    yield


app = FastAPI(title="Summarag API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    chroma_collection: str
    document_count: int


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    collection = get_collection()
    return HealthResponse(
        status="ok",
        chroma_collection=collection.name,
        document_count=collection.count(),
    )