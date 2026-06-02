"""
Loads application settings from environment variables and resolves storage paths.
"""

from pathlib import Path
from typing import Any

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = _BACKEND_ROOT.parent


class Settings(BaseSettings):
    """
    Holds configuration for the API, LLM providers, chunking, and file storage.

    Values are read from `.env` at the repo root and under `backend/`.
    """

    model_config = SettingsConfigDict(
        env_file=(
            str(_REPO_ROOT / ".env"),
            str(_BACKEND_ROOT / ".env"),
        ),
        extra="ignore",
    )

    llm_provider: str = "openai"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "llama3"

    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str | None = None

    chroma_persist_dir: str = "./chroma_db"
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"

    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k_chunks: int = 12
    max_file_size: int = 50 * 1024 * 1024
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_timeout: float = 120.0
    max_context_chars: int = 100000
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    @field_validator("llm_provider")
    @classmethod
    def normalize_provider(cls, value: str) -> str:
        """
        Normalizes the LLM provider name for consistent lookups.

        Args:
            value (str): Raw provider string from the environment.

        Returns:
            str: Lowercase, trimmed provider name.
        """
        return value.strip().lower()

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        """
        Parses cors_origins from a comma-separated string if provided from environment.
        """
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_overlap(self) -> "Settings":
        """
        Validates that chunk overlap is strictly less than chunk size.
        """
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return self

    def chroma_path(self) -> Path:
        """
        Resolves the on-disk directory used by ChromaDB.

        Returns:
            Path: Absolute path to the Chroma persistence folder.
        """
        path = Path(self.chroma_persist_dir)
        if not path.is_absolute():
            path = _BACKEND_ROOT / path
        return path

    def upload_path(self) -> Path:
        """
        Resolves the directory where uploaded files are stored.

        Returns:
            Path: Absolute path to the uploads folder.
        """
        path = Path(self.upload_dir)
        if not path.is_absolute():
            path = _BACKEND_ROOT / path
        return path

    def output_path(self) -> Path:
        """
        Resolves the directory where generated PDFs are written.

        Returns:
            Path: Absolute path to the outputs folder.
        """
        path = Path(self.output_dir)
        if not path.is_absolute():
            path = _BACKEND_ROOT / path
        return path


settings = Settings()
