"""Application settings loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Pydantic settings for the RAG summarizer backend."""

    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_ROOT / ".env"),
        extra="ignore",
    )

    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    llm_model: str = "llama3"

    chroma_persist_dir: str = "./chroma_db"
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"

    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k_chunks: int = 12
    max_file_size: int = 50 * 1024 * 1024

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
