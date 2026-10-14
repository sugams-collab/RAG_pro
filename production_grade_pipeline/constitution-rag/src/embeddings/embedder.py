"""
Production-grade embedding service.

Features
--------
- Batch embedding
- GPU/CPU auto detection
- Embedding normalization
- Progress logging
- Singleton model loading
"""

from __future__ import annotations

from typing import List

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from configs.logging import get_logger
from configs.settings import settings
from src.core.document import Document
from src.core.exceptions import EmbeddingError

logger = get_logger(__name__)


class EmbeddingService:
    _model: SentenceTransformer | None = None

    def __init__(self) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        if EmbeddingService._model is None:
            logger.info(
                "Loading embedding model: %s",
                settings.EMBEDDING_MODEL,
            )

            EmbeddingService._model = SentenceTransformer(
                settings.EMBEDDING_MODEL,
                device=self.device,
            )

        self.model = EmbeddingService._model

    def embed_documents(
        self,
        documents: List[Document],
    ) -> List[Document]:
        """
        Generate embeddings for a list of documents.
        """

        if not documents:
            return []

        texts = [doc.text for doc in documents]

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=settings.EMBEDDING_BATCH_SIZE,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=True,
            )

        except Exception as e:
            raise EmbeddingError(
                "Failed to generate embeddings."
            ) from e

        embedded_docs: List[Document] = []

        for doc, emb in zip(documents, embeddings):
            embedded_docs.append(
                doc.with_embedding(
                    emb.astype(np.float32).tolist()
                )
            )

        logger.info(
            "Generated embeddings for %d documents.",
            len(embedded_docs),
        )

        return embedded_docs

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Generate embedding for a search query.
        """

        try:
            embedding = self.model.encode(
                query,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )

            return embedding.astype(np.float32).tolist()

        except Exception as e:
            raise EmbeddingError(
                "Failed to embed query."
            ) from e