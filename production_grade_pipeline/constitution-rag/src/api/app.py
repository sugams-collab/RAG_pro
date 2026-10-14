"""
Production-grade FastAPI application for Hybrid RAG.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from configs.logging import get_logger
from configs.settings import settings
from src.api.schemas import (
    Citation,
    HealthResponse,
    QueryRequest,
    QueryResponse,
)
from src.rag.pipeline import HybridRAGPipeline

logger = get_logger(__name__)

pipeline: HybridRAGPipeline | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline

    logger.info("Initializing Hybrid RAG Pipeline...")

    pipeline = HybridRAGPipeline()

    logger.info("Pipeline initialized.")

    yield

    logger.info("Application shutdown.")


app = FastAPI(
    title="Hybrid RAG API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get(
    "/health",
    response_model=HealthResponse,
)
async def health():

    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Pipeline not initialized.",
        )

    return HealthResponse(
        status="healthy",
        llm=pipeline.llm.health_check(),
        vector_db=True,
        embedding_model=settings.EMBEDDING_MODEL,
    )


@app.post(
    "/query",
    response_model=QueryResponse,
)
async def query(request: QueryRequest):

    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Pipeline not initialized.",
        )

    result = pipeline.query(
        request.question,
    )

    citations = [
        Citation(
            document_id=doc.id,
            source=doc.metadata.source,
            page=doc.metadata.page,
            article=doc.metadata.article,
            score=doc.score,
        )
        for doc in result.documents
    ]

    return QueryResponse(
        answer=result.answer,
        citations=citations,
    )


@app.get("/")
async def root():

    return {
        "application": "Hybrid RAG",
        "version": "1.0.0",
        "status": "running",
    }