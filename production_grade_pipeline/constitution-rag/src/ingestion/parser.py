"""
Document parsers.

A parser enriches Documents with structural metadata
after the PDF loader has extracted raw text.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from configs.logging import get_logger
from src.core.document import Document

logger = get_logger(__name__)


class BaseParser(ABC):
    """
    Base interface for all document parsers.
    """

    @abstractmethod
    def parse(
        self,
        documents: list[Document],
    ) -> list[Document]:
        """
        Parse and enrich documents.
        """
        raise NotImplementedError


class ConstitutionParser(BaseParser):
    """
    Extract legal hierarchy from the Indian Constitution.
    """

    PART_PATTERN = re.compile(r"PART\s+([IVXLC]+)", re.IGNORECASE)

    CHAPTER_PATTERN = re.compile(
        r"CHAPTER\s+([IVXLC]+)",
        re.IGNORECASE,
    )

    ARTICLE_PATTERN = re.compile(
        r"Article\s+(\d+[A-Z]?)",
        re.IGNORECASE,
    )

    CLAUSE_PATTERN = re.compile(
        r"\((\d+)\)"
    )

    def parse(
        self,
        documents: list[Document],
    ) -> list[Document]:

        logger.info(
            "Parsing %d documents.",
            len(documents),
        )

        current_part = None
        current_chapter = None
        current_article = None

        for doc in documents:

            text = doc.text

            # -------------------------
            # Part
            # -------------------------

            match = self.PART_PATTERN.search(text)

            if match:
                current_part = match.group(1)

            # -------------------------
            # Chapter
            # -------------------------

            match = self.CHAPTER_PATTERN.search(text)

            if match:
                current_chapter = match.group(1)

            # -------------------------
            # Article
            # -------------------------

            match = self.ARTICLE_PATTERN.search(text)

            if match:
                current_article = match.group(1)

            # -------------------------
            # Clause
            # -------------------------

            clause_match = self.CLAUSE_PATTERN.search(text)

            if clause_match:
                doc.metadata.clause = clause_match.group(1)

            doc.metadata.part = current_part
            doc.metadata.chapter = current_chapter
            doc.metadata.article = current_article

        logger.info("Parsing complete.")

        return documents