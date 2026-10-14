"""
Production-grade Cross Encoder Reranker.

Re-ranks hybrid retrieval results using a CrossEncoder model.
"""

from __future__ import annotations

from sentence_transformers import CrossEncoder

from configs.logging import get_logger
from configs.settings import settings
from src.core.document import Document
from src.core.exceptions import RerankingError

logger = get_logger(__name__)


class CrossEncoderReranker:
    """
    Cross Encoder reranker.

    Example models
    --------------
    BAAI/bge-reranker-base
    BAAI/bge-reranker-large
    cross-encoder/ms-marco-MiniLM-L-6-v2
    """

    _model: CrossEncoder | None = None

    def __init__(self) -> None:

        if CrossEncoderReranker._model is None:

            logger.info(
                "Loading reranker model: %s",
                settings.RERANKER_MODEL,
            )

            CrossEncoderReranker._model = CrossEncoder(
                settings.RERANKER_MODEL,
                device=settings.DEVICE,
            )

        self.model = CrossEncoderReranker._model

    # ---------------------------------------------------------

    def rerank(
        self,
        query: str,
        documents: list[Document],
        top_k: int = 10,
    ) -> list[Document]:
        """
        Re-rank retrieved documents.
        """

        if not documents:
            return []

        try:

            pairs = [
                (query, doc.text)
                for doc in documents
            ]

            scores = self.model.predict(
                pairs,
                batch_size=settings.RERANKER_BATCH_SIZE,
                show_progress_bar=False,
            )

            ranked = sorted(
                zip(documents, scores),
                key=lambda x: x[1],
                reverse=True,
            )

            results = [
                doc.with_score(float(score))
                for doc, score in ranked[:top_k]
            ]

            logger.info(
                "Reranked %d documents.",
                len(results),
            )

            return results

        except Exception as e:

            raise RerankingError(
                "CrossEncoder reranking failed."
            ) from e