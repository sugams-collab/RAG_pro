"""
rag.py

Complete Retrieval-Augmented Generation pipeline.
"""

from langchain_ollama import ChatOllama

from reranker import hybrid_search


# ----------------------------------------
# Load LLM
# ----------------------------------------

llm = ChatOllama(
    model="minimax-m3:cloud",
    temperature=0
)


# ----------------------------------------
# Prompt Template
# ----------------------------------------

PROMPT = """
You are an AI assistant answering questions about the Indian Constitution.

Use ONLY the provided context.

If the answer is not present in the context,
reply:

"I couldn't find this information in the provided documents."

-----------------------------
Context:

{context}

-----------------------------

Question:

{question}

Answer:
"""


# ----------------------------------------
# Format Documents
# ----------------------------------------

def format_context(documents):

    context = ""

    for doc in documents:

        page = doc.metadata["page"]

        context += f"""

Page: {page}

{doc.page_content}

"""

    return context


# ----------------------------------------
# Build Citations
# ----------------------------------------

def build_citations(documents):

    citations = []

    seen = set()

    for doc in documents:

        page = doc.metadata["page"]

        source = doc.metadata["source"]

        key = (page, source)

        if key not in seen:

            citations.append(
                f"{source} (Page {page})"
            )

            seen.add(key)

    return citations


# ----------------------------------------
# Main Pipeline
# ----------------------------------------

def ask(question):

    # Retrieve documents
    docs = hybrid_search(question)

    # Build Context
    context = format_context(docs)

    # Build Prompt
    prompt = PROMPT.format(
        context=context,
        question=question
    )

    # Generate Answer
    response = llm.invoke(prompt)

    citations = build_citations(docs)

    return {
        "answer": response.content,
        "citations": citations,
        "documents": docs
    }


# ----------------------------------------
# Test
# ----------------------------------------

if __name__ == "__main__":

    result = ask(
        "What is Right to Equality?"
    )

    print()

    print(result["answer"])

    print()

    print("Sources")

    for source in result["citations"]:

        print("-", source)