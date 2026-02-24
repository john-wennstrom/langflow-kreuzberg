"""Error taxonomy for Kreuzberg components."""

from __future__ import annotations

import socket
from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorContext:
    """Context used to build user-facing extraction error messages."""

    component: str
    filename: str | None = None

    @property
    def file_label(self) -> str:
        return self.filename or "<unknown file>"


class KreuzbergComponentError(Exception):
    """Base exception with an actionable hint for users."""

    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message)
        self.hint = hint

    def __str__(self) -> str:
        text = super().__str__()
        if self.hint:
            return f"{text} Next step: {self.hint}"
        return text


class UnsupportedFormatError(KreuzbergComponentError):
    """Raised when input document format is unsupported."""


class OCRBackendMissingError(KreuzbergComponentError):
    """Raised when OCR backend is requested but unavailable."""


class CorruptDocumentError(KreuzbergComponentError):
    """Raised when document bytes cannot be parsed."""


class ExtractionTimeoutError(KreuzbergComponentError):
    """Raised when extraction exceeds configured timeout."""


class RemoteExtractionError(KreuzbergComponentError):
    """Raised when remote extraction dependencies fail."""


def map_extraction_exception(
    exc: Exception,
    *,
    component: str,
    filename: str | None,
) -> KreuzbergComponentError:
    """Map Kreuzberg/raw exceptions to the extraction error taxonomy."""

    if isinstance(exc, KreuzbergComponentError):
        return exc

    context = ErrorContext(component=component, filename=filename)
    error_name = exc.__class__.__name__.lower()
    detail = str(exc).strip() or "No error details were provided by the backend."
    detail_lower = detail.lower()

    if isinstance(exc, TimeoutError) or "timeout" in error_name or "timed out" in detail_lower:
        return ExtractionTimeoutError(
            (
                f"{context.component} failed while extracting '{context.file_label}' because the "
                "operation exceeded the configured timeout. Likely cause: OCR/extraction took too "
                f"long for this document. Backend detail: {detail}"
            ),
            hint="Increase timeout settings or retry with a smaller/simpler document.",
        )

    if isinstance(exc, (ConnectionError, socket.gaierror)) or any(
        token in detail_lower
        for token in ("http", "connection", "dns", "ssl", "503", "502", "remote")
    ):
        return RemoteExtractionError(
            (
                f"{context.component} failed while extracting '{context.file_label}' due to a "
                "remote service/network error. "
                "Likely cause: extraction server unavailable. "
                f"Backend detail: {detail}"
            ),
            hint=(
                "Verify remote extraction service health, URL, "
                "credentials, and network connectivity."
            ),
        )

    if isinstance(exc, ImportError) or "module not found" in detail_lower:
        return OCRBackendMissingError(
            (
                f"{context.component} could not extract '{context.file_label}' because the OCR "
                "backend is not installed. "
                "Likely cause: missing optional OCR dependency. "
                f"Backend detail: {detail}"
            ),
            hint="Install an OCR backend, e.g. `pip install kreuzberg[paddleocr]`.",
        )

    if any(token in detail_lower for token in ("unsupported", "mime", "format", "file type")):
        return UnsupportedFormatError(
            (
                f"{context.component} cannot process '{context.file_label}' because the document "
                "format is unsupported. "
                "Likely cause: the MIME/file type is not supported. "
                f"Backend detail: {detail}"
            ),
            hint="Convert the file to PDF, DOCX, HTML, PNG, or plain text before retrying.",
        )

    if any(
        token in detail_lower for token in ("corrupt", "invalid", "parse", "decode", "encrypted")
    ):
        return CorruptDocumentError(
            (
                f"{context.component} failed to parse '{context.file_label}'. "
                "Likely cause: the document is corrupt, encrypted, or unreadable. "
                f"Backend detail: {detail}"
            ),
            hint="Re-export or repair the file and retry extraction.",
        )

    return KreuzbergComponentError(
        (
            f"{context.component} failed while extracting '{context.file_label}'. "
            "Likely cause: an unexpected extraction backend error occurred. "
            f"Backend detail: {detail}"
        ),
        hint=(
            "Review backend logs and retry. If the issue persists, "
            "open a support ticket with this message."
        ),
    )
