"""
CLI interface for the Production Hybrid RAG system.
"""

from __future__ import annotations

import pickle

from configs.logging import get_logger
from configs.settings import settings
from src.embeddings.embedder import EmbeddingService
from src.llm.ollama_client import OllamaClient
from src.rag.pipeline import HybridRAGPipeline
from src.retrieval.cross_encoder import CrossEncoderReranker
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.vectorstore.chroma_store import ChromaVectorStore

logger = get_logger(__name__)


def build_pipeline() -> HybridRAGPipeline:
    """
    Build the pipeline with the persisted BM25 index.
    """

    embedder = EmbeddingService()

    vector_store = ChromaVectorStore()

    with open(
        settings.BM25_PATH,
        "rb",
    ) as f:

        bm25: BM25Retriever = pickle.load(f)

    retriever = HybridRetriever(
        vector_store=vector_store,
        bm25=bm25,
        embedder=embedder,
    )

    reranker = CrossEncoderReranker()

    llm = OllamaClient()

    pipeline = HybridRAGPipeline()

    pipeline.embedder = embedder
    pipeline.vector_store = vector_store
    pipeline.bm25 = bm25
    pipeline.retriever = retriever
    pipeline.reranker = reranker
    pipeline.llm = llm

    return pipeline


def main():

    logger.info("Loading Hybrid RAG...")

    pipeline = build_pipeline()

    print("\nHybrid RAG CLI")
    print("Type 'exit' to quit.\n")

    while True:

        question = input("Question > ").strip()

        if question.lower() in {
            "exit",
            "quit",
        }:
            break

        response = pipeline.query(question)

        print("\n==========================")
        print("Answer")
        print("==========================\n")

        print(response.answer)

        print("\n==========================")
        print("Sources")
        print("==========================\n")

        for i, doc in enumerate(
            response.documents,
            start=1,
        ):

            print(
                f"[{i}] "
                f"{doc.metadata.source} | "
                f"Page {doc.metadata.page} | "
                f"Article {doc.metadata.article} | "
                f"Score={doc.score:.4f}"
            )

        print()


if __name__ == "__main__":
    main()