"""Tests for the Kreuzberg Extract component."""

from __future__ import annotations

import pytest

from components.kreuzberg.kreuzberg_errors import CorruptDocumentError, UnsupportedFormatError
from components.kreuzberg.nodes.extract import KreuzbergExtractComponent


@pytest.fixture
def component() -> KreuzbergExtractComponent:
    return KreuzbergExtractComponent()


def test_extract_component_supports_html(component: KreuzbergExtractComponent) -> None:
    payload = {
        "bytes": b"<html><body><h1>Hello</h1><p>world</p></body></html>",
        "filename": "sample.html",
        "mime": "text/html",
        "source_id": "src-1",
    }

    result = component.build(document_source=payload, output_format="text")

    assert result["extracted_doc"]["text"] == "Hello world"
    assert result["extracted_doc"]["metadata"]["source_id"] == "src-1"
    assert result["run_report"]["item_count"] == 1


def test_extract_component_supports_docx_like_bytes(component: KreuzbergExtractComponent) -> None:
    payload = {
        "bytes": b"This is docx content",
        "filename": "sample.docx",
        "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "source_id": "src-docx",
    }

    result = component.build(document_source=payload)

    assert "docx content" in result["extracted_doc"]["text"]


def test_extract_component_supports_png_via_ocr(component: KreuzbergExtractComponent) -> None:
    payload = {
        "bytes": b"\x89PNG\r\n\x1a\n",
        "filename": "scan.png",
        "mime": "image/png",
        "source_id": "src-png",
    }

    result = component.build(document_source=payload, ocr_mode="auto", page_tracking=True)

    assert result["extracted_doc"]["metadata"]["ocr_used"] is True
    assert result["pages"][0]["metadata"]["page_number"] == 1


def test_extract_component_rejects_unsupported_format(component: KreuzbergExtractComponent) -> None:
    payload = {
        "bytes": b"{\"a\":1}",
        "filename": "data.json",
        "mime": "application/json",
    }

    with pytest.raises(UnsupportedFormatError, match="Unsupported document format"):
        component.build(document_source=payload)


def test_extract_component_requires_valid_bytes(component: KreuzbergExtractComponent) -> None:
    payload = {
        "bytes": "not-bytes",
        "filename": "broken.pdf",
        "mime": "application/pdf",
    }

    with pytest.raises(CorruptDocumentError, match="missing raw bytes"):
        component.build(document_source=payload)


def test_extract_component_defines_langflow_ports() -> None:
    component = KreuzbergExtractComponent()

    input_names = {item.name for item in component.inputs}
    output_names = {item.name for item in component.outputs}

    assert "document_source" in input_names
    assert "output_format" in input_names
    assert "run_report" in output_names
    assert "extracted_doc" in output_names


def test_extract_component_output_methods_return_data_wrapper(
    component: KreuzbergExtractComponent,
) -> None:
    payload = {
        "bytes": b"plain text",
        "filename": "sample.txt",
        "mime": "text/plain",
        "source_id": "src-plain",
    }

    component.build(document_source=payload)

    extracted_doc = component.build_extracted_doc()
    run_report = component.build_run_report()

    assert hasattr(extracted_doc, "data")
    assert extracted_doc.data["text"] == "plain text"
    assert run_report.data["item_count"] == 1
