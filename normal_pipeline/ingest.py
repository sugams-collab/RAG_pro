"""
ingest.py

Purpose:
--------
This file loads the Constitution PDF and converts every page
into a LangChain Document object.

Output:
-------
List[Document]

Each Document contains:
    - page_content
    - metadata
"""

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from typing import List
import re


# -------------------------------------------------------
# Text Cleaning Function
# -------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Cleans unwanted spaces and formatting.

    Parameters
    ----------
    text : str
        Raw extracted text.

    Returns
    -------
    str
        Cleaned text.
    """

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Remove multiple blank lines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# -------------------------------------------------------
# Load PDF
# -------------------------------------------------------

def load_pdf(pdf_path: str) -> List[Document]:
    """
    Loads a PDF.

    Parameters
    ----------
    pdf_path : str

    Returns
    -------
    List[Document]
    """

    loader = PyPDFLoader(pdf_path)

    documents = loader.load()

    cleaned_documents = []

    for doc in documents:

        cleaned_text = clean_text(doc.page_content)

        new_doc = Document(
            page_content=cleaned_text,

            metadata={
                "page": doc.metadata["page"] + 1,
                "source": pdf_path
            }
        )

        cleaned_documents.append(new_doc)

    return cleaned_documents


# -------------------------------------------------------
# Example Usage
# -------------------------------------------------------

if __name__ == "__main__":

    docs = load_pdf("/home/cis/windows/sugam/AI/projects/RAG/data/THE_CONSTITUTION_OF_INDIA.pdf")

    print(f"Loaded {len(docs)} pages")

    print("\nFirst Page\n")

    print(docs[0].page_content[:800])

    print("\nMetadata")

    print(docs[0].metadata)