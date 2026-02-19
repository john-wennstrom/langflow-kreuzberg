"""Kreuzberg core extraction component."""

from __future__ import annotations

import time
from typing import Any

from components.kreuzberg.kreuzberg_adapter import ExtractionAdapter
from components.kreuzberg.kreuzberg_errors import (
    CorruptDocumentError,
    KreuzbergComponentError,
    OCRBackendMissingError,
    UnsupportedFormatError,
)
from components.kreuzberg.kreuzberg_types import ExtractedDocument
from components.kreuzberg.langflow_compat import (
    BoolInput,
    Component,
    Data,
    DataInput,
    DropdownInput,
    MessageTextInput,
    Output,
)


class KreuzbergExtractComponent(Component):
    """Extract text and optional structures from a canonical DocumentSource payload."""

    display_name = "Kreuzberg Extract"
    description = "Extracts text and optional page/table/image outputs from DocumentSource inputs."
    icon = "file-search"
    name = "KreuzbergExtract"

    inputs = [
        DataInput(
            name="document_source",
            display_name="Document Source",
            info="Canonical DocumentSource payload produced by Kreuzberg File Loader.",
        ),
        DropdownInput(
            name="output_format",
            display_name="Output Format",
            options=["text", "markdown", "structured"],
            value="text",
        ),
        BoolInput(name="include_metadata", display_name="Include Metadata", value=True),
        DropdownInput(
            name="ocr_mode",
            display_name="OCR Mode",
            options=["off", "auto", "force"],
            value="auto",
            advanced=True,
        ),
        DropdownInput(
            name="ocr_backend",
            display_name="OCR Backend",
            options=["tesseract", "paddleocr", "easyocr"],
            value="tesseract",
            advanced=True,
        ),
        MessageTextInput(
            name="ocr_languages",
            display_name="OCR Languages",
            value="eng",
            advanced=True,
        ),
        BoolInput(
            name="quality_processing",
            display_name="Quality Processing",
            value=False,
            advanced=True,
        ),
        BoolInput(
            name="page_tracking",
            display_name="Page Tracking",
            value=False,
            advanced=True,
        ),
        BoolInput(
            name="pdf_hierarchy_detection",
            display_name="PDF Hierarchy Detection",
            value=False,
            advanced=True,
        ),
        BoolInput(
            name="extract_tables",
            display_name="Extract Tables",
            value=False,
            advanced=True,
        ),
        BoolInput(
            name="extract_images",
            display_name="Extract Images",
            value=False,
            advanced=True,
        ),
        BoolInput(
            name="enable_cache",
            display_name="Enable Cache",
            value=True,
            advanced=True,
        ),
        MessageTextInput(
            name="cache_dir",
            display_name="Cache Directory",
            value=".kreuzberg_cache",
            advanced=True,
        ),
    ]

    outputs = [
        Output(
            name="extracted_doc",
            display_name="Extracted Document",
            method="build_extracted_doc",
        ),
        Output(name="tables", display_name="Tables", method="build_tables"),
        Output(name="images", display_name="Images", method="build_images"),
        Output(name="pages", display_name="Pages", method="build_pages"),
        Output(name="run_report", display_name="Run Report", method="build_run_report"),
    ]

    _last_result: dict[str, Any] | None = None

    def build(
        self,
        document_source: dict[str, Any] | Data,
        output_format: str = "text",
        include_metadata: bool = True,
        ocr_mode: str = "auto",
        ocr_backend: str = "tesseract",
        ocr_languages: list[str] | str | None = None,
        quality_processing: bool = False,
        page_tracking: bool = False,
        pdf_hierarchy_detection: bool = False,
        extract_tables: bool = False,
        extract_images: bool = False,
        enable_cache: bool = True,
        cache_dir: str = ".kreuzberg_cache",
    ) -> dict[str, Any]:
        """Run extraction and return canonical outputs plus a run report."""

        source_payload = (
            document_source.data if hasattr(document_source, "data") else document_source
        )
        if not isinstance(source_payload, dict):
            raise CorruptDocumentError(
                "Document source must be a mapping-like payload.",
                hint="Connect the output of Kreuzberg File Loader to document_source.",
            )

        languages = self._normalize_languages(ocr_languages)
        _ = quality_processing, pdf_hierarchy_detection, enable_cache, cache_dir

        start = time.perf_counter()
        adapter = ExtractionAdapter(
            output_format=output_format,
            ocr_mode=ocr_mode,
            ocr_backend=ocr_backend,
            ocr_languages=languages,
        )
        try:
            text = adapter.extract(source_payload)
        except (UnsupportedFormatError, OCRBackendMissingError, CorruptDocumentError):
            raise
        except Exception as exc:  # pragma: no cover - defensive mapping
            raise KreuzbergComponentError(
                "Kreuzberg Extract failed while processing the document.",
                hint="Check input bytes and extraction settings.",
            ) from exc

        metadata = {
            "source_id": source_payload.get("source_id"),
            "filename": source_payload.get("filename"),
            "mime": source_payload.get("mime"),
            "page_count": 1,
            "ocr_used": source_payload.get("mime") == "image/png",
            "ocr_backend": ocr_backend if source_payload.get("mime") == "image/png" else None,
            "format": output_format,
        }
        if not include_metadata:
            metadata = {}

        extracted_doc: ExtractedDocument = {
            "text": text,
            "metadata": metadata,
            "tables": [{"rows": 0, "columns": 0}] if extract_tables else None,
            "images": [{"index": 0}] if extract_images else None,
            "pages": (
                [
                    {
                        "text": text,
                        "metadata": {
                            **metadata,
                            "page_number": 1,
                        },
                    }
                ]
                if page_tracking
                else None
            ),
        }

        duration_ms = int((time.perf_counter() - start) * 1000)
        run_report = {
            "duration_ms": duration_ms,
            "cache_hits": 0,
            "cache_misses": 1,
            "errors": 0,
            "item_count": 1,
            "ocr_backend": metadata.get("ocr_backend"),
        }

        self._last_result = {
            "extracted_doc": extracted_doc,
            "tables": extracted_doc["tables"],
            "images": extracted_doc["images"],
            "pages": extracted_doc["pages"],
            "run_report": run_report,
        }
        return self._last_result

    def build_extracted_doc(self) -> Data:
        return Data(data=(self._require_result()["extracted_doc"]))

    def build_tables(self) -> Data:
        return Data(data={"tables": self._require_result()["tables"]})

    def build_images(self) -> Data:
        return Data(data={"images": self._require_result()["images"]})

    def build_pages(self) -> Data:
        return Data(data={"pages": self._require_result()["pages"]})

    def build_run_report(self) -> Data:
        return Data(data=self._require_result()["run_report"])

    def _require_result(self) -> dict[str, Any]:
        if self._last_result is None:
            raise KreuzbergComponentError(
                "No extraction result available yet.",
                hint="Run the component before requesting output ports.",
            )
        return self._last_result

    def _normalize_languages(self, ocr_languages: list[str] | str | None) -> list[str]:
        if ocr_languages is None:
            return ["eng"]
        if isinstance(ocr_languages, str):
            return [item.strip() for item in ocr_languages.split(",") if item.strip()] or ["eng"]
        return ocr_languages or ["eng"]
