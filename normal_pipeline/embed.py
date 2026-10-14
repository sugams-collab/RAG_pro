"""
embed.py

Purpose
-------
Creates embeddings for every chunk and stores them
inside ChromaDB.

Input
-----
List[Document]

Output
------
Persistent Chroma Vector Database
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from ingest import load_pdf
from chunk import create_chunks


# -------------------------------------------------
# Create Embedding Model
# -------------------------------------------------

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",

    model_kwargs={
        "device": "cpu"
    },

    encode_kwargs={
        "normalize_embeddings": True
    }
)


# -------------------------------------------------
# Build Vector Database
# -------------------------------------------------

def build_vector_database():

    # Step 1
    docs = load_pdf("/home/cis/windows/sugam/AI/projects/RAG/data/THE_CONSTITUTION_OF_INDIA.pdf")

    # Step 2
    chunks = create_chunks(docs)

    # Step 3
    db = Chroma.from_documents(

        documents=chunks,

        embedding=embedding_model,

        persist_directory="chroma_db"

    )

    print(f"Stored {len(chunks)} chunks.")


if __name__ == "__main__":

    build_vector_database()