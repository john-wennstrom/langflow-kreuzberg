"""Kreuzberg file loader component."""

from __future__ import annotations

import mimetypes
from hashlib import sha256
from pathlib import Path
from typing import Any

from lfx.custom.custom_component.component import Component
from lfx.io import FileInput, Output, StrInput
from lfx.schema import Data

from components.kreuzberg.kreuzberg_types import DocumentSource
from components.kreuzberg.kreuzberg_utils import hash_id


class KreuzbergFileLoaderComponent(Component):
    """Load an uploaded file or file path into canonical DocumentSource payload."""

    display_name = "Kreuzberg File Loader"
    description = "Converts files into canonical DocumentSource payloads for extraction nodes."
    documentation = "https://github.com/kreuzberg-ai/langflow-kreuzberg"
    icon = "file"
    name = "KreuzbergFileLoader"

    inputs = [
        FileInput(
            name="file",
            display_name="File",
            info="Uploaded file from the Langflow UI.",
            required=False,
        ),
        StrInput(
            name="file_path",
            display_name="File Path",
            info="Absolute or relative local file path.",
            required=False,
        ),
        StrInput(name="filename_override", display_name="Filename Override", advanced=True),
        StrInput(name="mime_override", display_name="MIME Override", advanced=True),
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
        file: Any | None = None,
        file_path: str | None = None,
        filename_override: str | None = None,
        mime_override: str | None = None,
    ) -> DocumentSource:
        """Create a canonical document source payload from an upload or filesystem path."""
        if file is None and not file_path:
            raise ValueError("Kreuzberg File Loader requires either 'file' or 'file_path'.")

        source_uri: str | None = file_path
        filename = filename_override

        if file is not None:
            payload_bytes = self._read_uploaded_file(file)
            if not filename:
                filename = self._extract_upload_filename(file)
        else:
            path = Path(file_path or "")
            payload_bytes = path.read_bytes()
            if not filename:
                filename = path.name

        if not filename:
            filename = "unknown"

        mime = mime_override or self._guess_mime(filename=filename, source_uri=source_uri)
        content_hash = sha256(payload_bytes).hexdigest()

        payload: DocumentSource = {
            "bytes": payload_bytes,
            "filename": filename,
            "mime": mime,
            "source_id": hash_id(filename, content_hash),
            "source_uri": source_uri,
        }
        self._last_payload = payload
        self.status = f"Loaded {filename} ({mime})"
        return payload

    def build_document_source(self) -> Data:
        if self._last_payload is None:
            raise ValueError("No file has been loaded yet.")
        return Data(data=self._last_payload)

    def _read_uploaded_file(self, file: Any) -> bytes:
        if isinstance(file, bytes):
            return file
        if hasattr(file, "read"):
            data = file.read()
            if hasattr(file, "seek"):
                file.seek(0)
            if isinstance(data, bytes):
                return data
            if isinstance(data, str):
                return data.encode("utf-8")
        raise ValueError(
            "Unsupported upload type for 'file'. Provide bytes or a readable file object."
        )

    def _extract_upload_filename(self, file: Any) -> str | None:
        name = getattr(file, "name", None)
        if isinstance(name, str) and name.strip():
            return Path(name).name
        return None

    def _guess_mime(self, filename: str, source_uri: str | None) -> str:
        guessed, _ = mimetypes.guess_type(source_uri or filename)
        return guessed or "application/octet-stream"
