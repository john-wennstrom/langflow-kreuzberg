"""Tests for extraction error taxonomy and user-facing messages."""

from __future__ import annotations

from components.kreuzberg.kreuzberg_errors import (
    CorruptDocumentError,
    ExtractionTimeoutError,
    OCRBackendMissingError,
    RemoteExtractionError,
    UnsupportedFormatError,
    map_extraction_exception,
)


def test_error_string_includes_hint_for_user_next_step() -> None:
    error = UnsupportedFormatError(
        (
            "Kreuzberg Extract cannot process 'invoice.xls' because the document "
            "format is unsupported."
        ),
        hint="Convert the file to PDF.",
    )

    rendered = str(error)

    assert "unsupported" in rendered
    assert "Next step:" in rendered
    assert "Convert the file to PDF" in rendered


def test_map_exception_to_missing_ocr_error_has_actionable_message() -> None:
    mapped = map_extraction_exception(
        ImportError("ModuleNotFoundError: No module named 'paddleocr'"),
        component="Kreuzberg Extract",
        filename="scan.png",
    )

    assert isinstance(mapped, OCRBackendMissingError)
    message = str(mapped)
    assert "Kreuzberg Extract" in message
    assert "scan.png" in message
    assert "Likely cause" in message
    assert "pip install kreuzberg[paddleocr]" in message


def test_map_exception_to_unsupported_format_error_has_component_and_hint() -> None:
    mapped = map_extraction_exception(
        ValueError("Unsupported MIME format: application/x-msdownload"),
        component="Kreuzberg Extract",
        filename="payload.bin",
    )

    assert isinstance(mapped, UnsupportedFormatError)
    message = str(mapped)
    assert "payload.bin" in message
    assert "unsupported" in message.lower()
    assert "Next step" in message


def test_map_exception_to_corrupt_document_error_has_component_and_hint() -> None:
    mapped = map_extraction_exception(
        ValueError("Document parse failed: corrupt xref table"),
        component="Kreuzberg Extract",
        filename="broken.pdf",
    )

    assert isinstance(mapped, CorruptDocumentError)
    message = str(mapped)
    assert "broken.pdf" in message
    assert "Likely cause" in message
    assert "repair the file" in message


def test_map_exception_to_timeout_error_has_component_and_hint() -> None:
    mapped = map_extraction_exception(
        TimeoutError("Extraction timed out after 30s"),
        component="Kreuzberg Extract",
        filename="huge.pdf",
    )

    assert isinstance(mapped, ExtractionTimeoutError)
    message = str(mapped)
    assert "huge.pdf" in message
    assert "exceeded the configured timeout" in message
    assert "Increase timeout settings" in message


def test_map_exception_to_remote_error_has_component_and_hint() -> None:
    mapped = map_extraction_exception(
        ConnectionError("HTTP 503 service unavailable"),
        component="Kreuzberg HTTP Extract",
        filename="remote.docx",
    )

    assert isinstance(mapped, RemoteExtractionError)
    message = str(mapped)
    assert "Kreuzberg HTTP Extract" in message
    assert "remote.docx" in message
    assert "remote" in message.lower()
    assert "Verify remote extraction service" in message
