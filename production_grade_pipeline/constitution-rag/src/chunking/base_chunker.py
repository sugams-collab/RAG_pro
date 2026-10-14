"""
Base interface for all chunkers.

A chunker transforms large documents into smaller,
retrieval-friendly chunks while preserving metadata.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from configs.logging import get_logger
from src.core.document import Document

logger = get_logger(__name__)


class BaseChunker(ABC):
    """
    Abstract base class for all chunkers.
    """

    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def chunk(
        self,
        documents: list[Document],
    ) -> list[Document]:
        """
        Split documents into chunks.

        Parameters
        ----------
        documents:
            Input documents.

        Returns
        -------
        list[Document]
            Chunked documents.
        """
        raise NotImplementedError

    def _create_chunk(
        self,
        parent: Document,
        text: str,
        chunk_index: int,
    ) -> Document:
        """
        Create a new chunk while preserving metadata.
        """

        metadata = parent.metadata.model_copy(deep=True)

        metadata.chunk_index = chunk_index

        metadata.update_statistics(text)

        return Document(
            text=text,
            metadata=metadata,
        )