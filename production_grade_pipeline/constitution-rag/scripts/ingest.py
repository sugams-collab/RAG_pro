"""
Production-grade ingestion script.

Pipeline
--------
PDF(s)
    ↓
Loader
    ↓
Parser
    ↓
Cleaner
    ↓
Chunker
    ↓
Embeddings
    ↓
ChromaDB
    ↓
BM25 Index
"""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

from configs.logging import get_logger
from configs.settings import settings
from src.chunking.constitution_chunker import ConstitutionChunker
from src.embeddings.embedder import EmbeddingService
from src.ingestion.cleaner import TextCleaner
from src.ingestion.loader import PDFLoader
from src.ingestion.parser import ConstitutionParser
from src.retrieval.bm25 import BM25Retriever
from src.vectorstore.chroma_store import ChromaVectorStore

logger = get_logger(__name__)


def ingest(path: str) -> None:

    logger.info("Starting ingestion...")

    # -------------------------------------------------
    # Load
    # -------------------------------------------------

    loader = PDFLoader()

    documents = loader.load(path)

    logger.info(
        "Loaded %d pages.",
        len(documents),
    )

    # -------------------------------------------------
    # Parse
    # -------------------------------------------------

    parser = ConstitutionParser()

    documents = parser.parse(documents)

    # -------------------------------------------------
    # Clean
    # -------------------------------------------------

    cleaner = TextCleaner()

    documents = cleaner.clean(documents)

    # -------------------------------------------------
    # Chunk
    # -------------------------------------------------

    chunker = ConstitutionChunker(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )

    chunks = chunker.chunk(documents)

    logger.info(
        "Generated %d chunks.",
        len(chunks),
    )

    # -------------------------------------------------
    # Embed
    # -------------------------------------------------

    embedder = EmbeddingService()

    chunks = embedder.embed_documents(chunks)

    # -------------------------------------------------
    # Vector Store
    # -------------------------------------------------

    vector_store = ChromaVectorStore()

    vector_store.add_documents(chunks)

    logger.info(
        "Stored embeddings in ChromaDB."
    )

    # -------------------------------------------------
    # BM25
    # -------------------------------------------------

    bm25 = BM25Retriever()

    bm25.build(chunks)

    bm25_path = Path(settings.BM25_PATH)

    bm25_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        bm25_path,
        "wb",
    ) as f:

        pickle.dump(
            bm25,
            f,
        )

    logger.info(
        "BM25 index saved to %s",
        bm25_path,
    )

    logger.info("Ingestion completed successfully.")


# ---------------------------------------------------------


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--path",
        required=True,
        help="PDF file or directory.",
    )

    args = parser.parse_args()

    ingest(args.path)