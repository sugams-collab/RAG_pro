"""
Constitution-specific chunker.

Chunks are created around Articles and Clauses rather than
arbitrary character boundaries.
"""

from __future__ import annotations

import re

from configs.logging import get_logger
from src.chunking.base_chunker import BaseChunker
from src.chunking.recursive_chunker import RecursiveChunker
from src.core.document import Document

logger = get_logger(__name__)


class ConstitutionChunker(BaseChunker):
    """
    Chunk legal documents while preserving article boundaries.
    """

    ARTICLE_PATTERN = re.compile(
        r"(?=Article\s+\d+[A-Z]?)",
        re.IGNORECASE,
    )

    CLAUSE_PATTERN = re.compile(
        r"(?=\(\d+\))"
    )

    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:

        super().__init__(
            chunk_size,
            chunk_overlap,
        )

        self.fallback = RecursiveChunker(
            chunk_size,
            chunk_overlap,
        )

    # -----------------------------------------------------

    def chunk(
        self,
        documents: list[Document],
    ) -> list[Document]:

        logger.info(
            "Constitution chunking started."
        )

        chunks: list[Document] = []

        for document in documents:

            chunk_index = 0

            article_chunks = self._split_articles(
                document.text
            )

            for article in article_chunks:

                # Entire article fits
                if len(article) <= self.chunk_size:

                    chunks.append(
                        self._create_chunk(
                            parent=document,
                            text=article,
                            chunk_index=chunk_index,
                        )
                    )

                    chunk_index += 1
                    continue

                # Try splitting by clause
                clauses = self._split_clauses(article)

                if all(
                    len(c) <= self.chunk_size
                    for c in clauses
                ):

                    for clause in clauses:

                        chunks.append(
                            self._create_chunk(
                                parent=document,
                                text=clause,
                                chunk_index=chunk_index,
                            )
                        )

                        chunk_index += 1

                    continue

                # Fallback to recursive chunker
                temp_doc = self._create_chunk(
                    parent=document,
                    text=article,
                    chunk_index=chunk_index,
                )

                recursive_chunks = self.fallback.chunk(
                    [temp_doc]
                )

                for rc in recursive_chunks:

                    rc.metadata.chunk_index = chunk_index

                    chunks.append(rc)

                    chunk_index += 1

        logger.info(
            "Generated %d legal chunks.",
            len(chunks),
        )

        return chunks

    # -----------------------------------------------------

    def _split_articles(
        self,
        text: str,
    ) -> list[str]:

        articles = self.ARTICLE_PATTERN.split(text)

        return [
            a.strip()
            for a in articles
            if a.strip()
        ]

    # -----------------------------------------------------

    def _split_clauses(
        self,
        article: str,
    ) -> list[str]:

        clauses = self.CLAUSE_PATTERN.split(article)

        return [
            c.strip()
            for c in clauses
            if c.strip()
        ]