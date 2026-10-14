"""
Central configuration for the entire HybridRAG project.

Every configurable value should live here.

Advantages
----------
- Single source of truth
- Environment variable support
- Validation
- Easy testing
- Easy deployment
"""

from pathlib import Path

from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global project configuration.

    Values can come from

    1. .env file
    2. Environment variables
    3. Default values below
    """

    # ==========================================================
    # Project Information
    # ==========================================================

    PROJECT_NAME: str = "HybridRAG"

    VERSION: str = "1.0.0"

    DEBUG: bool = True

    # ==========================================================
    # Directories
    # ==========================================================

    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    DATA_DIR: Path = BASE_DIR / "data"

    RAW_DATA_DIR: Path = DATA_DIR / "raw"

    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"

    STORAGE_DIR: Path = BASE_DIR / "storage"

    CHROMA_DIR: Path = STORAGE_DIR / "chroma"

    BM25_PATH: Path = STORAGE_DIR / "bm25.pkl"

    LOG_DIR: Path = BASE_DIR / "logs"

    # ==========================================================
    # Embedding Model
    # ==========================================================

    EMBEDDING_MODEL: str = Field(
        default="BAAI/bge-base-en-v1.5"
    )

    EMBEDDING_DEVICE: str = "cpu"

    EMBEDDING_BATCH_SIZE: int = 32

    NORMALIZE_EMBEDDINGS: bool = True

    # ==========================================================
    # Vector Database
    # ==========================================================

    COLLECTION_NAME: str = "indian_constitution"

    CHROMA_DB_PATH: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "storage" / "chroma")

    # ==========================================================
    # Chunking
    # ==========================================================

    CHUNK_SIZE: int = 512

    CHUNK_OVERLAP: int = 64

    # ==========================================================
    # Retrieval
    # ==========================================================

    VECTOR_TOP_K: int = 20

    BM25_TOP_K: int = 20

    HYBRID_TOP_K: int = 25

    FINAL_TOP_K: int = 5

    # ==========================================================
    # Re-ranker
    # ==========================================================

    RERANKER_MODEL: str = "BAAI/bge-reranker-base"

    RERANKER_TOP_K: int = 8

    RERANKER_BATCH_SIZE: int = 16

    DEVICE: str = "cpu"

    # ==========================================================
    # LLM
    # ==========================================================

    LLM_PROVIDER: str = "ollama"

    OLLAMA_HOST: str = "http://localhost:11434"

    LLM_MODEL: str = "minimax-m3:cloud"

    TEMPERATURE: float = 0.0

    MAX_TOKENS: int = 2048

    SYSTEM_PROMPT: str = """You are a legal AI assistant specializing in the Indian Constitution.

Answer ONLY from the provided context.

If the answer cannot be found in the retrieved documents, say: 'I could not find the answer in the provided documents.'

Never hallucinate. Always be concise. Always preserve legal terminology."""

    # ==========================================================
    # API Server
    # ==========================================================

    HOST: str = "0.0.0.0"

    PORT: int = 8000

    WORKERS: int = 1

    # ==========================================================
    # Logging
    # ==========================================================

    LOG_LEVEL: str = "INFO"

    # ==========================================================
    # Cache
    # ==========================================================

    ENABLE_CACHE: bool = True

    CACHE_SIZE: int = 512

    # ==========================================================
    # Pydantic Settings Configuration
    # ==========================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()