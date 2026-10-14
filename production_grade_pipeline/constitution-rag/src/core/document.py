"""
Core document model used throughout the project.

Every stage of the pipeline operates on this object.

PDF
 ↓
Document
 ↓
Chunk
 ↓
Embedding
 ↓
Retrieval
 ↓
LLM
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    Represents one logical document or chunk.

    This class is intentionally generic so it can represent:

    - Entire PDF
    - Single page
    - Chunk
    - Retrieved result
    """

    # ---------------------------------------------------------
    # Unique ID
    # ---------------------------------------------------------

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique document identifier."
    )

    # ---------------------------------------------------------
    # Main Text
    # ---------------------------------------------------------

    text: str = Field(
        ...,
        min_length=1,
        description="Document content."
    )

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata."
    )

    # ---------------------------------------------------------
    # Retrieval Score
    # ---------------------------------------------------------

    score: float | None = Field(
        default=None,
        description="Retrieval or reranking score."
    )

    # ---------------------------------------------------------
    # Embedding
    # ---------------------------------------------------------

    embedding: list[float] | None = Field(
        default=None,
        description="Embedding vector."
    )

    # ---------------------------------------------------------
    # Helper Methods
    # ---------------------------------------------------------

    def with_score(self, score: float) -> "Document":
        """
        Return a copy with an updated score.
        """
        return self.model_copy(
            update={"score": score}
        )

    def with_embedding(
        self,
        embedding: list[float]
    ) -> "Document":
        """
        Return a copy with an embedding.
        """
        return self.model_copy(
            update={"embedding": embedding}
        )

    @property
    def page(self) -> int | None:
        return self.metadata.get("page")

    @property
    def source(self) -> str | None:
        return self.metadata.get("source")

    @property
    def article(self) -> str | None:
        return self.metadata.get("article")

    def short_text(
        self,
        length: int = 120
    ) -> str:
        """
        Return shortened text for logging.
        """

        if len(self.text) <= length:
            return self.text

        return self.text[:length] + "..."

    def __str__(self) -> str:

        return (
            f"Document("
            f"id={self.id[:8]}, "
            f"page={self.page}, "
            f"source={self.source})"
        )