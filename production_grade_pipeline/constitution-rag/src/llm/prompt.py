"""
Prompt templates for LLM generation.
"""

from __future__ import annotations


class PromptTemplate:
    """Base class for prompt templates."""

    def __init__(self, template: str):
        self.template = template

    def format(self, **kwargs) -> str:
        """Format the template with provided variables."""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(
                f"Missing required variable: {e}"
            )


class RAGPromptTemplate(PromptTemplate):
    """Prompt template for RAG queries."""

    DEFAULT_TEMPLATE = """You are an expert legal AI assistant specializing in the Indian Constituti/home/cis/windows/sugam/AI/projects/RAG/production_grade_pipeline/constitution-ragon.

Your task is to answer the user's question ONLY based on the provided context.

IMPORTANT RULES:
1. Answer ONLY from the provided context
2. If the answer cannot be found in the context, respond with: "I could not find the answer in the provided documents."
3. Never hallucinate or make up information
4. Always be concise and clear
5. Preserve legal terminology exactly as used in the Constitution
6. For every factual statement, cite the source document

CITATION FORMAT:
When citing, use this format: [Document X] or "as stated in Article X of Document Y"

---
CONTEXT:
{context}

---
QUESTION:
{question}

---
ANSWER:"""

    def __init__(self):
        super().__init__(self.DEFAULT_TEMPLATE)

    def build(
        self,
        context: str,
        question: str,
    ) -> str:
        """Build the prompt with context and question."""
        return self.format(
            context=context,
            question=question,
        )


class FollowUpPromptTemplate(PromptTemplate):
    """Prompt template for follow-up questions in conversation."""

    DEFAULT_TEMPLATE = """You are an expert legal AI assistant.

Based on this conversation history, answer the follow-up question.

PREVIOUS ANSWER:
{previous_answer}

NEW CONTEXT:
{context}

FOLLOW-UP QUESTION:
{question}

---
Answer based only on the provided context. If the answer cannot be found, say so explicitly."""

    def __init__(self):
        super().__init__(self.DEFAULT_TEMPLATE)

    def build(
        self,
        previous_answer: str,
        context: str,
        question: str,
    ) -> str:
        """Build follow-up prompt."""
        return self.format(
            previous_answer=previous_answer,
            context=context,
            question=question,
        )


class SummarizationPromptTemplate(PromptTemplate):
    """Prompt template for summarizing retrieved documents."""

    DEFAULT_TEMPLATE = """Summarize the following legal text from the Indian Constitution in 2-3 sentences while preserving key legal terminology:

TEXT:
{text}

---
SUMMARY:"""

    def __init__(self):
        super().__init__(self.DEFAULT_TEMPLATE)

    def build(self, text: str) -> str:
        """Build summarization prompt."""
        return self.format(text=text)


# Global prompt templates
RAG_PROMPT = RAGPromptTemplate()
FOLLOWUP_PROMPT = FollowUpPromptTemplate()
SUMMARIZATION_PROMPT = SummarizationPromptTemplate()
