"""
PDF document loader.

Loads one or multiple PDF files and converts each page
into a Document object with metadata.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import fitz  # PyMuPDF

from configs.logging import get_logger
from src.core.document import Document
from src.core.metadata import DocumentMetadata
from src.core.exceptions import PDFLoadError

logger = get_logger(__name__)


class PDFLoader:
    """
    Load PDF documents from disk.
    """

    def __init__(self) -> None:
        logger.info("PDFLoader initialized.")

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def load(self, path: str | Path) -> list[Document]:
        """
        Load a PDF file or a directory containing PDFs.
        """

        path = Path(path)

        if not path.exists():
            raise PDFLoadError(f"Path does not exist: {path}")

        if path.is_dir():
            return self._load_directory(path)

        if path.suffix.lower() != ".pdf":
            raise PDFLoadError(f"Unsupported file: {path}")

        return self._load_pdf(path)

    # ---------------------------------------------------------
    # Directory Loader
    # ---------------------------------------------------------

    def _load_directory(
        self,
        directory: Path,
    ) -> list[Document]:

        documents: list[Document] = []

        pdfs = sorted(directory.glob("*.pdf"))

        logger.info(
            "Found %d PDF files.",
            len(pdfs),
        )

        for pdf in pdfs:
            documents.extend(self._load_pdf(pdf))

        return documents

    # ---------------------------------------------------------
    # Single PDF
    # ---------------------------------------------------------

    def _load_pdf(
        self,
        pdf_path: Path,
    ) -> list[Document]:

        logger.info("Loading %s", pdf_path.name)

        try:

            pdf = fitz.open(pdf_path)

        except Exception as e:
            raise PDFLoadError(
                f"Unable to open {pdf_path}"
            ) from e

        checksum = self._checksum(pdf_path)

        documents: list[Document] = []

        for page_number, page in enumerate(pdf, start=1):

            text = page.get_text("text")

            metadata = DocumentMetadata(
                source=pdf_path.name,
                source_path=str(pdf_path.resolve()),
                page=page_number,
                checksum=checksum,
            )

            metadata.update_statistics(text)

            doc = Document(
                text=text,
                metadata=metadata,
            )

            documents.append(doc)

        logger.info(
            "%s loaded (%d pages).",
            pdf_path.name,
            len(documents),
        )

        return documents

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _checksum(path: Path) -> str:
        """
        SHA256 checksum of the file.
        """

        sha = hashlib.sha256()

        with path.open("rb") as f:

            while chunk := f.read(8192):
                sha.update(chunk)

        return sha.hexdigest()