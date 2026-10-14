"""
Extended API endpoints for the Hybrid RAG system.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from configs.logging import get_logger
from src.rag.pipeline import HybridRAGPipeline
from src.utils.cache import QueryCache
from src.utils.timer import PipelineTimer

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1")

# Global instances
pipeline: HybridRAGPipeline | None = None
query_cache = QueryCache(max_size=512)
timer = PipelineTimer()


class DocumentInfo(BaseModel):
    """Information about a retrieved document."""

    document_id: str
    source: str
    article: int | None = None
    page: int | None = None
    score: float


class BatchQueryRequest(BaseModel):
    """Request for batch querying."""

    questions: list[str]


class BatchQueryResponse(BaseModel):
    """Response for batch querying."""

    results: list[dict]
    total_time_ms: float


@router.get("/health")
async def extended_health():
    """Extended health check with component details."""
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Pipeline not initialized.",
        )

    return {
        "status": "healthy",
        "components": {
            "llm": pipeline.llm.health_check(),
            "vector_db": True,
            "embedding": True,
            "reranker": True,
        },
        "cache": query_cache.stats(),
    }


@router.post("/query/batch")
async def batch_query(request: BatchQueryRequest):
    """Process multiple queries at once."""
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Pipeline not initialized.",
        )

    timer.start("batch_query")
    results = []

    for i, question in enumerate(request.questions):
        try:
            # Check cache first
            cached = query_cache.get(question)
            if cached:
                results.append(
                    {
                        "question": question,
                        "answer": cached["answer"],
                        "cached": True,
                    }
                )
            else:
                result = pipeline.query(question)
                answer_data = {
                    "question": question,
                    "answer": result.answer,
                    "cached": False,
                    "num_documents": len(result.documents),
                }
                query_cache.set(question, answer_data)
                results.append(answer_data)

        except Exception as e:
            logger.error(
                f"Error processing question {i}: {e}"
            )
            results.append(
                {
                    "question": question,
                    "error": str(e),
                }
            )

    elapsed_ms = timer.end() * 1000

    return BatchQueryResponse(
        results=results,
        total_time_ms=elapsed_ms,
    )


@router.get("/query/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    return query_cache.stats()


@router.post("/query/cache/clear")
async def clear_cache():
    """Clear the query cache."""
    query_cache.clear()
    return {"status": "cleared"}


@router.get("/performance/timings")
async def get_timings():
    """Get performance timings summary."""
    return {"summary": timer.summary()}


@router.get("/models/info")
async def model_info():
    """Get information about deployed models."""
    from configs.settings import settings

    return {
        "embedding_model": settings.EMBEDDING_MODEL,
        "embedding_device": settings.EMBEDDING_DEVICE,
        "embedding_batch_size": settings.EMBEDDING_BATCH_SIZE,
        "reranker_model": settings.RERANKER_MODEL,
        "reranker_top_k": settings.RERANKER_TOP_K,
        "reranker_batch_size": settings.RERANKER_BATCH_SIZE,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "temperature": settings.TEMPERATURE,
    }


@router.post("/search/similar")
async def search_similar(request: dict):
    """Search for similar documents based on query."""
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Pipeline not initialized.",
        )

    query = request.get("query", "")
    top_k = request.get("top_k", 10)

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query parameter required",
        )

    try:
        docs = pipeline.retriever.search(query=query, top_k=top_k)

        return {
            "query": query,
            "documents": [
                {
                    "id": doc.id,
                    "text": doc.text[:200],
                    "score": doc.score,
                    "source": doc.metadata.source,
                    "article": doc.metadata.article,
                    "page": doc.metadata.page,
                }
                for doc in docs
            ],
        }

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/stats")
async def get_stats():
    """Get system statistics."""
    return {
        "cache": query_cache.stats(),
        "timings": timer.summary(),
    }
