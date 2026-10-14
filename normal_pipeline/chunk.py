"""
chunk.py

Purpose
-------
Split long documents into smaller chunks while
preserving metadata.

Input
-----
List[Document]

Output
------
List[Document]
"""

from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_chunks(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Document]:
    """
    Split documents into smaller chunks.

    Parameters
    ----------
    documents : List[Document]

    chunk_size : int

    chunk_overlap : int

    Returns
    -------
    List[Document]
    """

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=chunk_size,

        chunk_overlap=chunk_overlap,

        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = splitter.split_documents(documents)

    for i, chunk in enumerate(chunks):

        chunk.metadata["chunk_id"] = i

    return chunks


if __name__ == "__main__":

    from ingest import load_pdf

    docs = load_pdf("/home/cis/windows/sugam/AI/projects/RAG/data/THE_CONSTITUTION_OF_INDIA.pdf")

    chunks = create_chunks(docs)

    print("Pages :", len(docs))

    print("Chunks:", len(chunks))

    print()

    print(chunks[0].page_content)

    print()

    print(chunks[0].metadata)