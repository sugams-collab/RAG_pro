"""
retriever.py

Hybrid Retriever

This module combines

1. Semantic Search (Chroma)

2. BM25 Search

into one retrieval pipeline.
"""

from typing import List

from langchain_core.documents import Document

from langchain_chroma import Chroma

from langchain_huggingface import HuggingFaceEmbeddings

from bm25 import build_bm25


# -------------------------------------
# Embedding model
# -------------------------------------

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"
)


# -------------------------------------
# Load Chroma Database
# -------------------------------------

vector_db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding_model
)


# -------------------------------------
# Load BM25
# -------------------------------------

bm25 = build_bm25()


# -------------------------------------
# Hybrid Search
# -------------------------------------

def hybrid_search(
    query: str,
    vector_k: int = 5,
    bm25_k: int = 5
) -> List[Document]:

    """
    Performs hybrid search.

    Parameters
    ----------

    query

    vector_k

    bm25_k

    Returns

    -------

    List[Document]
    """

    # ---------------------------
    # Vector Search
    # ---------------------------

    vector_results = vector_db.similarity_search(
        query,
        k=vector_k
    )

    # ---------------------------
    # BM25 Search
    # ---------------------------

    bm25.k = bm25_k

    bm25_results = bm25.invoke(query)

    # ---------------------------
    # Merge Results
    # ---------------------------

    combined = vector_results + bm25_results

    # ---------------------------
    # Remove duplicates
    # ---------------------------

    unique_docs = {}

    for doc in combined:

        chunk_id = doc.metadata["chunk_id"]

        if chunk_id not in unique_docs:

            unique_docs[chunk_id] = doc

    return list(unique_docs.values())


# -------------------------------------
# Test
# -------------------------------------

if __name__ == "__main__":

    docs = hybrid_search(
        "What is Article 21?"
    )

    print()

    print(f"Retrieved {len(docs)} documents")

    print()

    for doc in docs:

        print("=" * 80)

        print(doc.metadata)

        print()

        print(doc.page_content[:300])