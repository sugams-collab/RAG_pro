"""
Citation formatting utilities.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core.document import Document


@dataclass
class FormattedCitation:
    """A formatted citation."""

    document_id: str
    text: str
    short_form: str


class CitationFormatter:
    """Formats citations for legal documents."""

    @staticmethod
    def format_inline(doc: Document) -> str:
        """Format citation for inline use in text."""
        parts = []

        if doc.metadata.source:
            parts.append(doc.metadata.source)

        if doc.metadata.article:
            parts.append(f"Article {doc.metadata.article}")

        if doc.metadata.page and doc.metadata.page > 0:
            parts.append(f"p. {doc.metadata.page}")

        if not parts:
            parts.append(f"Document {doc.id}")

        return ", ".join(parts)

    @staticmethod
    def format_footnote(doc: Document) -> str:
        """Format citation as a footnote."""
        parts = []

        if doc.metadata.source:
            parts.append(f"Source: {doc.metadata.source}")

        if doc.metadata.part:
            parts.append(f"Part {doc.metadata.part}")

        if doc.metadata.chapter:
            parts.append(f"Chapter {doc.metadata.chapter}")

        if doc.metadata.article:
            parts.append(f"Article {doc.metadata.article}")

        if doc.metadata.page and doc.metadata.page > 0:
            parts.append(f"Page {doc.metadata.page}")

        if doc.score is not None and doc.score > 0:
            parts.append(f"(Relevance: {doc.score:.2f})")

        return " | ".join(parts)

    @staticmethod
    def format_hierarchical(doc: Document) -> str:
        """Format citation showing full hierarchical structure."""
        parts = []

        if doc.metadata.source:
            parts.append(doc.metadata.source)

        hierarchy = []
        if doc.metadata.part:
            hierarchy.append(f"Part {doc.metadata.part}")
        if doc.metadata.chapter:
            hierarchy.append(f"Chapter {doc.metadata.chapter}")
        if doc.metadata.article:
            hierarchy.append(f"Article {doc.metadata.article}")

        if hierarchy:
            parts.append(" → ".join(hierarchy))

        if doc.metadata.page and doc.metadata.page > 0:
            parts.append(f"[Page {doc.metadata.page}]")

        return " | ".join(parts)

    @staticmethod
    def format_mla(doc: Document) -> str:
        """Format citation in MLA style."""
        source = doc.metadata.source or "Unknown Source"

        if doc.metadata.article:
            return f"{source}, Article {doc.metadata.article}"

        if doc.metadata.page and doc.metadata.page > 0:
            return f"{source}, p. {doc.metadata.page}"

        return source

    @staticmethod
    def format_apa(doc: Document) -> str:
        """Format citation in APA style."""
        source = doc.metadata.source or "Unknown Source"

        if doc.metadata.article:
            article_num = doc.metadata.article
            if doc.metadata.page and doc.metadata.page > 0:
                return f"{source}, Article {article_num} (p. {doc.metadata.page})"
            return f"{source}, Article {article_num}"

        if doc.metadata.page and doc.metadata.page > 0:
            return f"{source}, {doc.metadata.page}"

        return source

    @staticmethod
    def format_chicago(doc: Document) -> str:
        """Format citation in Chicago style."""
        source = doc.metadata.source or "Unknown Source"
        parts = [source]

        if doc.metadata.part:
            parts.append(f"Part {doc.metadata.part}")

        if doc.metadata.article:
            parts.append(f"Art. {doc.metadata.article}")

        if doc.metadata.page and doc.metadata.page > 0:
            parts.append(f"at {doc.metadata.page}")

        return ", ".join(parts)

    @staticmethod
    def format_document_list(
        documents: list[Document],
        format_type: str = "inline",
    ) -> list[str]:
        """Format a list of documents."""
        formatter_map = {
            "inline": CitationFormatter.format_inline,
            "footnote": CitationFormatter.format_footnote,
            "hierarchical": CitationFormatter.format_hierarchical,
            "mla": CitationFormatter.format_mla,
            "apa": CitationFormatter.format_apa,
            "chicago": CitationFormatter.format_chicago,
        }

        formatter = formatter_map.get(
            format_type,
            CitationFormatter.format_inline,
        )

        return [formatter(doc) for doc in documents]

    @staticmethod
    def build_bibliography(
        documents: list[Document],
    ) -> str:
        """Build a complete bibliography from documents."""
        unique_sources = {}

        for doc in documents:
            source = doc.metadata.source or "Unknown"
            if source not in unique_sources:
                unique_sources[source] = []
            if doc.metadata.article:
                unique_sources[source].append(
                    doc.metadata.article
                )

        bibliography_items = []
        for source in sorted(unique_sources.keys()):
            articles = sorted(set(unique_sources[source]))
            if articles:
                articles_str = ", ".join(
                    f"Article {a}" for a in articles if a
                )
                bibliography_items.append(
                    f"{source} ({articles_str})"
                )
            else:
                bibliography_items.append(source)

        return "\n".join(bibliography_items)
