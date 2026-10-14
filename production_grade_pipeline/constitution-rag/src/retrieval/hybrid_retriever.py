"""
Production-grade Hybrid Retriever.

Combines:
- Dense Vector Search (ChromaDB)
- Sparse BM25 Search
- Reciprocal Rank Fusion (RRF)

Output:
    List[Document]
"""

from __future__ import annotations

from collections import defaultdict

from configs.logging import get_logger
from src.core.document import Document
from src.core.exceptions import VectorStoreError
from src.embeddings.embedder import EmbeddingService
from src.retrieval.bm25 import BM25Retriever
from src.vectorstore.chroma_store import ChromaVectorStore

logger = get_logger(__name__)


class HybridRetriever:
    """
    Hybrid Retriever using

    Dense Search
        +
    BM25
        +
    Reciprocal Rank Fusion (RRF)
    """

    def __init__(
        self,
        vector_store: ChromaVectorStore,
        bm25: BM25Retriever,
        embedder: EmbeddingService,
        rrf_k: int = 60,
    ) -> None:

        self.vector_store = vector_store
        self.bm25 = bm25
        self.embedder = embedder
        self.rrf_k = rrf_k

    # ---------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 10,
        dense_k: int = 30,
        sparse_k: int = 30,
    ) -> list[Document]:

        # Validate inputs
        if not query:
            logger.warning("Empty query received")
            return []

        if top_k <= 0 or dense_k <= 0 or sparse_k <= 0:
            logger.warning("Invalid top_k values")
            return []

        try:
            # -----------------------------------------------------
            # Dense Search
            # -----------------------------------------------------

            query_embedding = self.embedder.embed_query(query)

            dense_results = self.vector_store.similarity_search(
                embedding=query_embedding,
                k=dense_k,
            )

            dense_docs = self._parse_dense_results(
                dense_results
            )

            logger.info(
                "Dense search returned %d documents.",
                len(dense_docs),
            )

        except Exception as e:
            logger.warning(f"Dense search failed: {e}")
            dense_docs = []

        try:
            # -----------------------------------------------------
            # Sparse Search
            # -----------------------------------------------------

            sparse_docs = self.bm25.search(
                query=query,
                top_k=sparse_k,
            )

            logger.info(
                "Sparse search returned %d documents.",
                len(sparse_docs),
            )

        except Exception as e:
            logger.warning(f"Sparse search failed: {e}")
            sparse_docs = []

        if not dense_docs and not sparse_docs:
            logger.warning("Both dense and sparse searches failed")
            return []

        # If only one method worked, return its results
        if not dense_docs:
            logger.info("Using only sparse search results")
            return sparse_docs[:top_k]

        if not sparse_docs:
            logger.info("Using only dense search results")
            return dense_docs[:top_k]

        # -----------------------------------------------------
        # Reciprocal Rank Fusion
        # -----------------------------------------------------

        fused = self._rrf(
            dense_docs,
            sparse_docs,
        )

        logger.info(
            "Hybrid search returned %d documents.",
            len(fused[:top_k]),
        )

        return fused[:top_k]

    # ---------------------------------------------------------

    def _rrf(
        self,
        dense: list[Document],
        sparse: list[Document],
    ) -> list[Document]:

        scores = defaultdict(float)
        lookup = {}

        for rank, doc in enumerate(dense):

            scores[doc.id] += 1.0 / (
                self.rrf_k + rank + 1
            )

            lookup[doc.id] = doc

        for rank, doc in enumerate(sparse):

            scores[doc.id] += 1.0 / (
                self.rrf_k + rank + 1
            )

            lookup[doc.id] = doc

        ranked = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        results = []

        for doc_id, score in ranked:

            results.append(
                lookup[doc_id].with_score(score)
            )

        return results

    # ---------------------------------------------------------

    @staticmethod
    def _parse_dense_results(
        results: dict,
    ) -> list[Document]:
        """Parse dense search results with error handling."""

        docs = []

        try:
            # Validate result structure
            if not results:
                logger.warning("Empty results received from vector store")
                return docs

            if "ids" not in results or "documents" not in results:
                raise VectorStoreError(
                    "Invalid result structure from vector store"
                )

            # Extract components with bounds checking
            if not results["ids"] or not results["ids"][0]:
                logger.info("No results returned from vector store")
                return docs

            ids = results["ids"][0]
            texts = results["documents"][0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            # Validate array lengths match
            if not (len(ids) == len(texts)):
                logger.warning(
                    "Mismatched result lengths: ids=%d, texts=%d",
                    len(ids),
                    len(texts),
                )
                min_len = min(len(ids), len(texts))
                ids = ids[:min_len]
                texts = texts[:min_len]

            if len(metas) < len(ids):
                logger.warning(
                    "Fewer metadatas than documents: %d vs %d",
                    len(metas),
                    len(ids),
                )
                metas = metas + [{}] * (len(ids) - len(metas))

            if len(distances) < len(ids):
                logger.warning(
                    "Fewer distances than documents: %d vs %d",
                    len(distances),
                    len(ids),
                )
                distances = distances + [0.0] * (len(ids) - len(distances))

            # Create documents
            for doc_id, text, meta, distance in zip(
                ids,
                texts,
                metas,
                distances,
            ):
                try:
                    # Validate data types and values
                    if not doc_id or not text:
                        logger.warning("Empty doc_id or text")
                        continue

                    # Ensure distance is valid
                    if not isinstance(distance, (int, float)):
                        distance = 0.0
                    else:
                        distance = max(0.0, min(1.0, distance))

                    score = 1 - distance

                    docs.append(
                        Document(
                            id=str(doc_id),
                            text=str(text),
                            metadata=meta if meta else {},
                            score=score,
                        )
                    )

                except Exception as e:
                    logger.warning(
                        f"Error creating document: {e}"
                    )
                    continue

        except Exception as e:
            raise VectorStoreError(
                f"Failed to parse dense results: {e}"
            ) from e

        return docs