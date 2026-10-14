"""
Query result caching system.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Optional

from configs.logging import get_logger

logger = get_logger(__name__)


class QueryCache:
    """Simple in-memory cache for query results."""

    def __init__(self, max_size: int = 512):
        self.max_size = max_size
        self.cache: dict[str, Any] = {}
        self.access_order: list[str] = []

    @staticmethod
    def _hash_query(query: str) -> str:
        """Create a hash of the query."""
        return hashlib.md5(query.encode()).hexdigest()

    def get(self, query: str) -> Optional[Any]:
        """Get cached result for query."""
        key = self._hash_query(query)

        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            logger.debug(f"Cache hit for query: {query[:50]}...")
            return self.cache[key]

        logger.debug(f"Cache miss for query: {query[:50]}...")
        return None

    def set(self, query: str, result: Any) -> None:
        """Cache a query result."""
        key = self._hash_query(query)

        if key in self.cache:
            # Update existing entry
            self.access_order.remove(key)
        else:
            # Check if we need to evict
            if len(self.cache) >= self.max_size:
                self._evict_oldest()

        self.cache[key] = result
        self.access_order.append(key)
        logger.debug(
            f"Cached query: {query[:50]}... (size: {len(self.cache)})"
        )

    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        self.access_order.clear()
        logger.info("Cache cleared")

    def _evict_oldest(self) -> None:
        """Remove the oldest (least recently used) entry."""
        if self.access_order:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
            logger.debug(f"Evicted old cache entry")

    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "fill_percentage": (
                len(self.cache) / self.max_size * 100
            ),
        }


class PersistentQueryCache:
    """Persistent file-based cache for query results."""

    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        self.memory_cache = QueryCache()

        try:
            import pathlib

            pathlib.Path(cache_dir).mkdir(
                parents=True,
                exist_ok=True,
            )
        except Exception as e:
            logger.warning(
                f"Could not create cache directory: {e}"
            )

    @staticmethod
    def _hash_query(query: str) -> str:
        """Create a hash of the query."""
        return hashlib.md5(query.encode()).hexdigest()

    def _get_cache_file(self, query: str) -> str:
        """Get the cache file path for a query."""
        import pathlib

        key = self._hash_query(query)
        return str(
            pathlib.Path(self.cache_dir) / f"{key}.json"
        )

    def get(self, query: str) -> Optional[Any]:
        """Get cached result (check memory first, then disk)."""
        # Check memory cache first
        result = self.memory_cache.get(query)
        if result is not None:
            return result

        # Check disk cache
        try:
            cache_file = self._get_cache_file(query)
            import pathlib

            if pathlib.Path(cache_file).exists():
                with open(cache_file, "r") as f:
                    result = json.load(f)
                    self.memory_cache.set(query, result)
                    logger.debug(
                        f"Loaded from disk cache: {query[:50]}..."
                    )
                    return result
        except Exception as e:
            logger.warning(f"Error reading cache file: {e}")

        return None

    def set(self, query: str, result: Any) -> None:
        """Cache a result (both memory and disk)."""
        self.memory_cache.set(query, result)

        try:
            cache_file = self._get_cache_file(query)
            with open(cache_file, "w") as f:
                json.dump(result, f, indent=2, default=str)
                logger.debug(
                    f"Saved to disk cache: {query[:50]}..."
                )
        except Exception as e:
            logger.warning(
                f"Error writing to cache file: {e}"
            )

    def clear(self) -> None:
        """Clear both memory and disk cache."""
        self.memory_cache.clear()

        try:
            import pathlib

            cache_dir = pathlib.Path(self.cache_dir)
            for cache_file in cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("Persistent cache cleared")
        except Exception as e:
            logger.warning(f"Error clearing disk cache: {e}")

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        try:
            import pathlib

            disk_size = len(
                list(pathlib.Path(self.cache_dir).glob("*.json"))
            )
        except Exception:
            disk_size = 0

        return {
            **self.memory_cache.stats(),
            "disk_cache_size": disk_size,
        }
