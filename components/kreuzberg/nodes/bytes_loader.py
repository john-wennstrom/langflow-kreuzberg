"""Kreuzberg bytes loader component."""

from __future__ import annotations

import base64
import binascii
import mimetypes

from lfx.custom.custom_component.component import Component
from lfx.io import DropdownInput, Output, StrInput
from lfx.schema import Data

from components.kreuzberg.kreuzberg_types import DocumentSource
from components.kreuzberg.kreuzberg_utils import hash_id


class KreuzbergBytesLoaderComponent(Component):
    """Convert raw byte strings or base64 payloads into DocumentSource data."""

    display_name = "Kreuzberg Bytes Loader"
    description = "Converts raw bytes/base64 strings into canonical DocumentSource payloads."
    documentation = "https://github.com/kreuzberg-ai/langflow-kreuzberg"
    icon = "binary"
    name = "KreuzbergBytesLoader"

    inputs = [
        StrInput(
            name="data_input",
            display_name="Data Input",
            info="Raw byte string or base64-encoded payload.",
            required=True,
        ),
        DropdownInput(
            name="input_format",
            display_name="Input Format",
            options=["bytes_str", "base64"],
            value="bytes_str",
            required=True,
        ),
        StrInput(
            name="filename",
            display_name="Filename",
            info="Filename to attach to this document source.",
            required=True,
            value="unknown",
        ),
        StrInput(
            name="mime",
            display_name="MIME",
            info="Optional MIME override. If blank, MIME is inferred from filename.",
            required=False,
            advanced=True,
        ),
    ]

    outputs = [
        Output(
            name="document_source",
            display_name="Document Source",
            method="build_document_source",
        )
    ]

    _last_payload: DocumentSource | None = None

    def build(
        self,
        data_input: str,
        input_format: str = "bytes_str",
        filename: str = "unknown",
        mime: str | None = None,
    ) -> DocumentSource:
        """Build a canonical document source from string bytes or base64 input."""
        normalized_filename = filename.strip() or "unknown"

        if input_format == "bytes_str":
            decoded_bytes = data_input.encode("utf-8")
        elif input_format == "base64":
            decoded_bytes = self._decode_base64(data_input)
        else:
            raise ValueError("input_format must be one of: bytes_str, base64")

        resolved_mime = mime or self._guess_mime(normalized_filename)
        payload: DocumentSource = {
            "bytes": decoded_bytes,
            "filename": normalized_filename,
            "mime": resolved_mime,
            "source_id": hash_id(normalized_filename, decoded_bytes),
            "source_uri": None,
        }
        self._last_payload = payload
        self.status = f"Loaded {normalized_filename} ({resolved_mime})"
        return payload

    def build_document_source(self) -> Data:
        """Return the generated document source as a Langflow Data object."""
        if self._last_payload is None:
            raise ValueError("No byte payload has been loaded yet.")
        return Data(data=self._last_payload)

    def _decode_base64(self, data_input: str) -> bytes:
        compact = "".join(data_input.split())
        missing_padding = (-len(compact)) % 4
        if missing_padding:
            compact = f"{compact}{'=' * missing_padding}"

        try:
            return base64.b64decode(compact, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError(
                "Invalid base64 input: ensure the payload is properly base64-encoded "
                "and includes correct padding characters (=)."
            ) from exc

    def _guess_mime(self, filename: str) -> str:
        guessed, _ = mimetypes.guess_type(filename)
        return guessed or "application/octet-stream"
