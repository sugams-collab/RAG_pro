"""
bm25.py

Purpose
-------
Creates a BM25 index from document chunks.

Input
-----
List[Document]

Output
------
BM25Retriever
"""

from langchain_community.retrievers import BM25Retriever

from ingest import load_pdf
from chunk import create_chunks


def build_bm25():

    # Load PDF
    docs = load_pdf("/home/cis/windows/sugam/AI/projects/RAG/data/THE_CONSTITUTION_OF_INDIA.pdf")

    # Split into chunks
    chunks = create_chunks(docs)

    # Create BM25 Retriever
    bm25 = BM25Retriever.from_documents(chunks)

    # Number of documents to retrieve
    bm25.k = 5

    return bm25


if __name__ == "__main__":

    retriever = build_bm25()

    query = "Article 370"

    results = retriever.invoke(query)

    for doc in results:

        print("=" * 80)

        print(doc.page_content)

        print(doc.metadata)