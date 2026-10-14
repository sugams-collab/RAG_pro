"""
Custom exception hierarchy for HybridRAG.

Every module should raise these exceptions instead
of generic Exception.
"""

from __future__ import annotations


class HybridRAGError(Exception):
    """
    Base class for all project exceptions.
    """

    pass


# ==========================================================
# Configuration
# ==========================================================

class ConfigurationError(HybridRAGError):
    """
    Invalid project configuration.
    """

    pass


# ==========================================================
# Document
# ==========================================================

class DocumentError(HybridRAGError):
    """
    Base document exception.
    """

    pass


class PDFLoadError(DocumentError):
    """
    PDF could not be loaded.
    """

    pass


class ParsingError(DocumentError):
    """
    Failed to parse document.
    """

    pass


class ChunkingError(DocumentError):
    """
    Chunk generation failed.
    """

    pass


# ==========================================================
# Embeddings
# ==========================================================

class EmbeddingError(HybridRAGError):
    """
    Embedding generation failed.
    """

    pass


# ==========================================================
# Vector Store
# ==========================================================

class VectorStoreError(HybridRAGError):
    """
    Vector database failure.
    """

    pass


# ==========================================================
# Retrieval
# ==========================================================

class RetrievalError(HybridRAGError):
    """
    Retrieval pipeline failure.
    """

    pass


# ==========================================================
# Reranker
# ==========================================================

class RerankingError(HybridRAGError):
    """
    CrossEncoder failed.
    """

    pass


# ==========================================================
# Prompt
# ==========================================================

class PromptError(HybridRAGError):
    """
    Prompt construction failed.
    """

    pass


# ==========================================================
# LLM
# ==========================================================

class LLMError(HybridRAGError):
    """
    LLM inference failed.
    """

    pass


# ==========================================================
# Citation
# ==========================================================

class CitationError(HybridRAGError):
    """
    Citation generation failed.
    """

    pass