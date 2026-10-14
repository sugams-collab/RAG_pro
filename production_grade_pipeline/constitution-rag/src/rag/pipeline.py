"""
Production-grade Hybrid RAG Pipeline.

Pipeline
--------
User Query
    ↓
Embedding
    ↓
Hybrid Retrieval (Dense + BM25)
    ↓
CrossEncoder Reranking
    ↓
Prompt Building
    ↓
LLM
    ↓
Answer + Citations
"""

from __future__ import annotations

from dataclasses import dataclass

from configs.logging import get_logger
from configs.settings import settings
from src.core.document import Document
from src.embeddings.embedder import EmbeddingService
from src.llm.ollama_client import OllamaClient
from src.retrieval.cross_encoder import CrossEncoderReranker
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.vectorstore.chroma_store import ChromaVectorStore

logger = get_logger(__name__)


@dataclass
class RAGResponse:
    answer: str
    documents: list[Document]


class HybridRAGPipeline:
    """
    End-to-end Hybrid RAG Pipeline.
    """

    def __init__(self) -> None:

        self.embedder = EmbeddingService()

        self.vector_store = ChromaVectorStore()

        self.bm25 = BM25Retriever()

        self.retriever = HybridRetriever(
            vector_store=self.vector_store,
            bm25=self.bm25,
            embedder=self.embedder,
        )

        self.reranker = CrossEncoderReranker()

        self.llm = OllamaClient()

    # ---------------------------------------------------------

    def query(
        self,
        question: str,
    ) -> RAGResponse:

        retrieved_docs = self.retriever.search(
            query=question,
            top_k=settings.HYBRID_TOP_K,
        )

        reranked_docs = self.reranker.rerank(
            query=question,
            documents=retrieved_docs,
            top_k=settings.RERANKER_TOP_K,
        )

        prompt = self._build_prompt(
            question,
            reranked_docs,
        )

        answer = self.llm.generate(
            prompt=prompt,
            system_prompt=settings.SYSTEM_PROMPT,
            temperature=0.0,
        )

        return RAGResponse(
            answer=answer,
            documents=reranked_docs,
        )

    # ---------------------------------------------------------

    def _build_prompt(
        self,
        question: str,
        documents: list[Document],
    ) -> str:

        context = []

        for idx, doc in enumerate(documents, start=1):

            citation = (
                f"{doc.metadata.source}, "
                f"Page {doc.metadata.page}"
            )

            if doc.metadata.article:
                citation += (
                    f", Article {doc.metadata.article}"
                )

            context.append(
                f"""
[Document {idx}]
Citation: {citation}

Content:
{doc.text}
"""
            )

        context_text = "\n\n".join(context)

        return f"""
Answer the question ONLY using the provided context.

If the answer is not present in the context,
reply exactly:

"I could not find the answer in the provided documents."

For every factual statement, cite the document number.

Example:
The Constitution guarantees equality before law [Document 2].

-------------------------
Context
-------------------------

{context_text}

-------------------------
Question
-------------------------

{question}

-------------------------
Answer
-------------------------
"""