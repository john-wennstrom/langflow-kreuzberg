"""Kreuzberg file loader component."""

from __future__ import annotations

import mimetypes
from hashlib import sha256
from pathlib import Path
from typing import Any

from components.kreuzberg.kreuzberg_types import DocumentSource
from components.kreuzberg.kreuzberg_utils import hash_id


class KreuzbergFileLoaderComponent:
    """Load a file (uploaded object or file path) into the canonical DocumentSource schema."""

    display_name = "Kreuzberg File Loader"
    description = "Converts files into canonical DocumentSource payloads for extraction nodes."
    icon = "file"
    name = "KreuzbergFileLoader"

    def build(
        self,
        file: Any | None = None,
        file_path: str | None = None,
        filename_override: str | None = None,
        mime_override: str | None = None,
    ) -> DocumentSource:
        """Create a canonical document source payload from an upload or filesystem path."""

        if file is None and not file_path:
            raise ValueError(
                "Kreuzberg File Loader requires either 'file' or 'file_path'."
            )

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

        return {
            "bytes": payload_bytes,
            "filename": filename,
            "mime": mime,
            "source_id": hash_id(filename, content_hash),
            "source_uri": source_uri,
        }

    def _read_uploaded_file(self, file: Any) -> bytes:
        if isinstance(file, bytes):
            return file

        if hasattr(file, "read"):
            file_obj = file
            data = file_obj.read()
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
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
