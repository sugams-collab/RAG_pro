"""
Pydantic request/response schemas for the Hybrid RAG API.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="User question.",
    )


class Citation(BaseModel):
    document_id: str
    source: str
    page: int | None = None
    article: str | None = None
    score: float | None = None


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]


class HealthResponse(BaseModel):
    status: str
    llm: bool
    vector_db: bool
    embedding_model: str