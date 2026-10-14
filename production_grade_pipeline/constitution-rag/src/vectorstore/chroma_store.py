"""
Production-grade ChromaDB vector store.
"""

from __future__ import annotations

from typing import List

import chromadb
from chromadb.config import Settings

from configs.logging import get_logger
from configs.settings import settings
from src.core.document import Document
from src.core.exceptions import VectorStoreError

logger = get_logger(__name__)


class ChromaVectorStore:
    def __init__(self) -> None:
        try:
            self.client = chromadb.PersistentClient(
                path=str(settings.CHROMA_DB_PATH),
                settings=Settings(
                    anonymized_telemetry=False,
                ),
            )

            self.collection = self.client.get_or_create_collection(
                name=settings.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )

            logger.info(
                "Connected to ChromaDB collection '%s'.",
                settings.COLLECTION_NAME,
            )

        except Exception as e:
            raise VectorStoreError(
                "Failed to initialize ChromaDB."
            ) from e

    # ---------------------------------------------------------

    def add_documents(
        self,
        documents: List[Document],
    ) -> None:

        if not documents:
            return

        try:
            self.collection.add(
                ids=[
                    doc.id
                    for doc in documents
                ],
                documents=[
                    doc.text
                    for doc in documents
                ],
                embeddings=[
                    doc.embedding
                    for doc in documents
                ],
                metadatas=[
                    {
                        "source": doc.metadata.source,
                        "page": doc.metadata.page,
                        "article": doc.metadata.article,
                        "chapter": doc.metadata.chapter,
                        "part": doc.metadata.part,
                        "chunk_index": doc.metadata.chunk_index,
                    }
                    for doc in documents
                ],
            )

            logger.info(
                "Inserted %d documents.",
                len(documents),
            )

        except Exception as e:
            raise VectorStoreError(
                "Failed to insert documents."
            ) from e

    # ---------------------------------------------------------

    def similarity_search(
        self,
        embedding: list[float],
        k: int = 10,
    ):

        try:
            return self.collection.query(
                query_embeddings=[embedding],
                n_results=k,
            )

        except Exception as e:
            raise VectorStoreError(
                "Vector search failed."
            ) from e

    # ---------------------------------------------------------

    def delete_collection(self):

        self.client.delete_collection(
            settings.collection_name
        )

    # ---------------------------------------------------------

    def count(self) -> int:

        return self.collection.count()