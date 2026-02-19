"""Error taxonomy for Kreuzberg components."""

from __future__ import annotations


class KreuzbergComponentError(Exception):
    """Base exception with an actionable hint for users."""

    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message)
        self.hint = hint


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
