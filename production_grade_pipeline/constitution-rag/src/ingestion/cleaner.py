"""
Text cleaning utilities.

The cleaner normalizes extracted text while preserving
the semantic meaning of the document.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from configs.logging import get_logger
from src.core.document import Document

logger = get_logger(__name__)


class BaseCleaner(ABC):
    """
    Base interface for all text cleaners.
    """

    @abstractmethod
    def clean(
        self,
        documents: list[Document],
    ) -> list[Document]:
        raise NotImplementedError


class TextCleaner(BaseCleaner):
    """
    Default text cleaner.

    Safe for legal and general documents.
    """

    MULTIPLE_SPACES = re.compile(r"[ \t]+")
    MULTIPLE_NEWLINES = re.compile(r"\n{3,}")
    PAGE_NUMBER = re.compile(r"^\s*\d+\s*$", re.MULTILINE)

    def clean(
        self,
        documents: list[Document],
    ) -> list[Document]:

        logger.info(
            "Cleaning %d documents.",
            len(documents),
        )

        for doc in documents:

            cleaned = self._clean_text(doc.text)

            doc.text = cleaned

            doc.metadata.update_statistics(cleaned)

        logger.info("Cleaning completed.")

        return documents

    def _clean_text(
        self,
        text: str,
    ) -> str:
        """
        Apply all cleaning operations.
        """

        text = self._normalize_line_endings(text)

        text = self._remove_page_numbers(text)

        text = self._collapse_spaces(text)

        text = self._collapse_blank_lines(text)

        text = text.strip()

        return text

    @staticmethod
    def _normalize_line_endings(
        text: str,
    ) -> str:
        """
        Convert Windows/Mac line endings to Unix.
        """

        return text.replace("\r\n", "\n").replace("\r", "\n")

    def _remove_page_numbers(
        self,
        text: str,
    ) -> str:
        """
        Remove standalone page numbers.

        Example

        42

        becomes

        ""
        """

        return self.PAGE_NUMBER.sub("", text)

    def _collapse_spaces(
        self,
        text: str,
    ) -> str:
        """
        Replace multiple spaces with one.
        """

        return self.MULTIPLE_SPACES.sub(" ", text)

    def _collapse_blank_lines(
        self,
        text: str,
    ) -> str:
        """
        Replace 3+ blank lines with two.
        """

        return self.MULTIPLE_NEWLINES.sub("\n\n", text)