"""
Recursive text chunker.

Splits text by:
1. Paragraphs
2. Sentences
3. Words

while preserving metadata.
"""

from __future__ import annotations

import re

from configs.logging import get_logger
from src.chunking.base_chunker import BaseChunker
from src.core.document import Document

logger = get_logger(__name__)


class RecursiveChunker(BaseChunker):
    """
    Recursive chunker that preserves semantic boundaries.
    """

    SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
    WORD_SPLIT = re.compile(r"\s+")

    def chunk(
        self,
        documents: list[Document],
    ) -> list[Document]:

        logger.info(
            "Chunking %d documents.",
            len(documents),
        )

        chunks: list[Document] = []

        for doc in documents:

            chunk_index = 0

            for text in self._split_document(doc.text):

                chunks.append(
                    self._create_chunk(
                        parent=doc,
                        text=text,
                        chunk_index=chunk_index,
                    )
                )

                chunk_index += 1

        logger.info(
            "Created %d chunks.",
            len(chunks),
        )

        return chunks

    # -------------------------------------------------

    def _split_document(
        self,
        text: str,
    ) -> list[str]:

        paragraphs = text.split("\n\n")

        chunks = []

        current = ""

        for paragraph in paragraphs:

            candidate = (
                paragraph
                if not current
                else current + "\n\n" + paragraph
            )

            if len(candidate) <= self.chunk_size:

                current = candidate

                continue

            if current:

                chunks.append(current)

            if len(paragraph) <= self.chunk_size:

                current = paragraph

            else:

                chunks.extend(
                    self._split_paragraph(paragraph)
                )

                current = ""

        if current:

            chunks.append(current)

        return self._apply_overlap(chunks)

    # -------------------------------------------------

    def _split_paragraph(
        self,
        paragraph: str,
    ) -> list[str]:

        sentences = self.SENTENCE_SPLIT.split(paragraph)

        chunks = []

        current = ""

        for sentence in sentences:

            candidate = (
                sentence
                if not current
                else current + " " + sentence
            )

            if len(candidate) <= self.chunk_size:

                current = candidate

                continue

            if current:

                chunks.append(current)

            if len(sentence) <= self.chunk_size:

                current = sentence

            else:

                chunks.extend(
                    self._split_sentence(sentence)
                )

                current = ""

        if current:

            chunks.append(current)

        return chunks

    # -------------------------------------------------

    def _split_sentence(
        self,
        sentence: str,
    ) -> list[str]:

        words = self.WORD_SPLIT.split(sentence)

        chunks = []

        current = ""

        for word in words:

            candidate = (
                word
                if not current
                else current + " " + word
            )

            if len(candidate) <= self.chunk_size:

                current = candidate

            else:

                chunks.append(current)

                current = word

        if current:

            chunks.append(current)

        return chunks

    # -------------------------------------------------

    def _apply_overlap(
        self,
        chunks: list[str],
    ) -> list[str]:

        if self.chunk_overlap <= 0:

            return chunks

        overlapped = []

        for i, chunk in enumerate(chunks):

            if i == 0:

                overlapped.append(chunk)

                continue

            previous = chunks[i - 1]

            overlap = previous[-self.chunk_overlap:]

            overlapped.append(
                overlap + "\n" + chunk
            )

        return overlapped