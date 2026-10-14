from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"
)

db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding_model
)

query = "Article 370"

results = db.similarity_search(query, k=3)

for doc in results:

    print("="*80)

    print(doc.page_content)

    print()

    print(doc.metadata)