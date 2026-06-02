"""Application settings loaded from environment variables."""

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = _BACKEND_ROOT.parent


class Settings(BaseSettings):
    """Pydantic settings for the RAG summarizer backend."""

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

    @field_validator("llm_provider")
    @classmethod
    def normalize_provider(cls, value: str) -> str:
        """Normalize provider name to lowercase."""
        return value.strip().lower()

    def chroma_path(self) -> Path:
        """Return resolved Chroma persistence directory."""
        path = Path(self.chroma_persist_dir)
        if not path.is_absolute():
            path = _BACKEND_ROOT / path
        return path

    def upload_path(self) -> Path:
        """Return resolved upload directory."""
        path = Path(self.upload_dir)
        if not path.is_absolute():
            path = _BACKEND_ROOT / path
        return path

    def output_path(self) -> Path:
        """Return resolved output directory."""
        path = Path(self.output_dir)
        if not path.is_absolute():
            path = _BACKEND_ROOT / path
        return path


settings = Settings()
