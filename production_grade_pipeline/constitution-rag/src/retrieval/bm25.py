"""
Production-grade BM25 retriever.

Uses rank-bm25 for lexical retrieval.
"""

from __future__ import annotations

from typing import List

from rank_bm25 import BM25Okapi

from configs.logging import get_logger
from src.core.document import Document
from src.core.exceptions import RetrievalError

logger = get_logger(__name__)


class BM25Retriever:
    """
    BM25 lexical retriever.

    Build once after ingestion and reuse for queries.
    """

    def __init__(self) -> None:
        self.documents: List[Document] = []
        self.corpus: List[List[str]] = []
        self.bm25: BM25Okapi | None = None

    # ---------------------------------------------------------

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """
        Simple whitespace tokenizer.

        Replace with spaCy/tokenizer later if needed.
        """
        return text.lower().split()

    # ---------------------------------------------------------

    def build(
        self,
        documents: List[Document],
    ) -> None:
        """
        Build BM25 index.
        """

        if not documents:
            raise RetrievalError(
                "Cannot build BM25 index with no documents."
            )

        self.documents = documents

        self.corpus = [
            self._tokenize(doc.text)
            for doc in documents
        ]

        self.bm25 = BM25Okapi(self.corpus)

        logger.info(
            "BM25 index built with %d documents.",
            len(documents),
        )

    # ---------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> List[Document]:
        """
        Retrieve top-k BM25 documents.
        """

        if self.bm25 is None:
            raise RetrievalError(
                "BM25 index has not been built."
            )

        query_tokens = self._tokenize(query)

        scores = self.bm25.get_scores(query_tokens)

        ranked = sorted(
            zip(self.documents, scores),
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]

        results = [
            doc.with_score(float(score))
            for doc, score in ranked
        ]

        logger.info(
            "BM25 returned %d documents.",
            len(results),
        )

        return results