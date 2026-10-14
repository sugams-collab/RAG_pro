"""
Strongly typed metadata model.

Every document/chunk carries metadata that is used
throughout retrieval, filtering, and citation generation.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """
    Metadata associated with a document or chunk.
    """

    # --------------------------------------------------
    # Source Information
    # --------------------------------------------------

    source: str = Field(
        ...,
        description="Original filename."
    )

    source_path: str | None = Field(
        default=None,
        description="Absolute path to the source file."
    )

    # --------------------------------------------------
    # Location
    # --------------------------------------------------

    page: int | None = Field(
        default=None,
        ge=1,
        description="Page number in original document."
    )

    chunk_index: int | None = Field(
        default=None,
        ge=0,
        description="Chunk index within the document."
    )

    # --------------------------------------------------
    # Hierarchical Metadata
    # --------------------------------------------------

    part: str | None = None

    chapter: str | None = None

    section: str | None = None

    article: str | None = None

    clause: str | None = None

    # --------------------------------------------------
    # Document Information
    # --------------------------------------------------

    title: str | None = None

    language: str = "en"

    author: str | None = None

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    char_count: int = 0

    word_count: int = 0

    token_count: int | None = None

    # --------------------------------------------------
    # Tracking
    # --------------------------------------------------

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    checksum: str | None = None

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    @property
    def filename(self) -> str:
        """
        Return only the filename.
        """

        return Path(self.source).name

    @property
    def citation(self) -> str:
        """
        Human readable citation.
        """

        pieces = []

        if self.article:
            pieces.append(f"Article {self.article}")

        if self.page:
            pieces.append(f"Page {self.page}")

        if not pieces:
            return self.filename

        return f"{self.filename} ({', '.join(pieces)})"

    def update_statistics(
        self,
        text: str
    ) -> None:
        """
        Automatically update character
        and word counts.
        """

        self.char_count = len(text)

        self.word_count = len(text.split())