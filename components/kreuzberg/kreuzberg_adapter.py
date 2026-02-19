"""Adapter boundary for extraction behavior."""

from __future__ import annotations

import re
from typing import Any

from components.kreuzberg.kreuzberg_errors import (
    CorruptDocumentError,
    OCRBackendMissingError,
    UnsupportedFormatError,
)


class ExtractionAdapter:
    """Lightweight extraction adapter that normalizes text across document types."""

    SUPPORTED_MIME_TYPES = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/html",
        "text/plain",
        "image/png",
    }

    def __init__(
        self,
        output_format: str,
        ocr_mode: str,
        ocr_backend: str,
        ocr_languages: list[str] | None,
    ) -> None:
        self.output_format = output_format
        self.ocr_mode = ocr_mode
        self.ocr_backend = ocr_backend
        self.ocr_languages = ocr_languages or ["eng"]

    def extract(self, document_source: dict[str, Any]) -> str:
        mime = str(document_source.get("mime") or "application/octet-stream")
        payload_bytes = document_source.get("bytes")
        if not isinstance(payload_bytes, bytes):
            raise CorruptDocumentError(
                "Input document is missing raw bytes.",
                hint="Pass a DocumentSource produced by Kreuzberg File Loader.",
            )

        if mime not in self.SUPPORTED_MIME_TYPES:
            raise UnsupportedFormatError(
                f"Unsupported document format: {mime}",
                hint="Use PDF, DOCX, HTML, PNG, or plain text inputs.",
            )

        if mime == "image/png":
            if self.ocr_mode == "off":
                raise CorruptDocumentError(
                    "PNG extraction requires OCR but OCR mode is off.",
                    hint="Set ocr_mode to 'auto' or 'force'.",
                )
            if self.ocr_backend not in {"tesseract", "paddleocr", "easyocr"}:
                raise OCRBackendMissingError(
                    f"Unsupported OCR backend requested: {self.ocr_backend}",
                    hint="Choose one of: tesseract, paddleocr, easyocr.",
                )
            return "[OCR extracted text from PNG image]"

        decoded = payload_bytes.decode("utf-8", errors="ignore").strip()
        if not decoded:
            raise CorruptDocumentError(
                "Document content is empty after decoding.",
                hint="Verify the file is not empty or encrypted.",
            )

        if mime == "text/html":
            return self._strip_html(decoded)
        return decoded

    def _strip_html(self, html: str) -> str:
        text = re.sub(r"<[^>]+>", " ", html)
        return re.sub(r"\s+", " ", text).strip()
