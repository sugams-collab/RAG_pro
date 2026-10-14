"""
Enhanced logging utilities.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from configs.logging import get_logger


class ContextLogger:
    """Logger with context information."""

    def __init__(self, name: str):
        self.logger = get_logger(name)
        self.context: dict[str, Any] = {}

    def set_context(self, **kwargs) -> None:
        """Set context variables."""
        self.context.update(kwargs)

    def clear_context(self) -> None:
        """Clear context."""
        self.context.clear()

    def _format_message(self, message: str) -> str:
        """Format message with context."""
        if not self.context:
            return message

        context_str = " | ".join(
            f"{k}={v}" for k, v in self.context.items()
        )
        return f"[{context_str}] {message}"

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(self._format_message(message), **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(self._format_message(message), **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(
            self._format_message(message), **kwargs
        )

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(self._format_message(message), **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(
            self._format_message(message), **kwargs
        )


class QueryLogger:
    """Specialized logger for query operations."""

    def __init__(self, query: str):
        self.logger = get_logger("query")
        self.query = query[:100] + "..." if len(query) > 100 else query
        self.query_id = id(query)  # Unique identifier

    def log_start(self) -> None:
        """Log query start."""
        self.logger.info(
            f"Query started [id={self.query_id}]: {self.query}"
        )

    def log_retrieval(
        self,
        stage: str,
        count: int,
        time_ms: float,
    ) -> None:
        """Log retrieval stage."""
        self.logger.info(
            f"[id={self.query_id}] {stage}: "
            f"retrieved {count} documents in {time_ms:.2f}ms"
        )

    def log_reranking(self, count: int, time_ms: float) -> None:
        """Log reranking."""
        self.logger.info(
            f"[id={self.query_id}] Reranked to {count} documents "
            f"in {time_ms:.2f}ms"
        )

    def log_generation(self, time_ms: float) -> None:
        """Log LLM generation."""
        self.logger.info(
            f"[id={self.query_id}] Generated answer in {time_ms:.2f}ms"
        )

    def log_complete(self, total_time_ms: float) -> None:
        """Log query completion."""
        self.logger.info(
            f"[id={self.query_id}] Query completed in {total_time_ms:.2f}ms"
        )

    def log_error(self, stage: str, error: Exception) -> None:
        """Log error during query processing."""
        self.logger.error(
            f"[id={self.query_id}] Error in {stage}: {error}"
        )


class PerformanceLogger:
    """Log performance metrics."""

    def __init__(self):
        self.logger = get_logger("performance")

    def log_embedding_stats(
        self,
        num_documents: int,
        time_seconds: float,
        batch_size: int,
    ) -> None:
        """Log embedding statistics."""
        throughput = num_documents / time_seconds if time_seconds > 0 else 0
        self.logger.info(
            f"Embedded {num_documents} docs in {time_seconds:.2f}s "
            f"(batch_size={batch_size}, throughput={throughput:.0f} docs/s)"
        )

    def log_retrieval_stats(
        self,
        vector_count: int,
        bm25_count: int,
        hybrid_count: int,
        time_ms: float,
    ) -> None:
        """Log retrieval statistics."""
        self.logger.info(
            f"Retrieval: vector={vector_count}, bm25={bm25_count}, "
            f"hybrid={hybrid_count} in {time_ms:.2f}ms"
        )

    def log_memory_usage(self, memory_mb: float) -> None:
        """Log memory usage."""
        self.logger.info(f"Memory usage: {memory_mb:.2f} MB")

    def log_cache_stats(
        self,
        hits: int,
        misses: int,
        size: int,
    ) -> None:
        """Log cache statistics."""
        hit_rate = hits / (hits + misses) if (hits + misses) > 0 else 0
        self.logger.info(
            f"Cache: hits={hits}, misses={misses}, "
            f"hit_rate={hit_rate:.1%}, size={size}"
        )
