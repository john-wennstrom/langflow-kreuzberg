"""Tests for the Kreuzberg file loader component."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest

from components.kreuzberg.nodes.file_loader import KreuzbergFileLoaderComponent


def test_file_loader_supports_file_path_input(tmp_path: Path) -> None:
    source_file = tmp_path / "sample.txt"
    source_file.write_text("hello from path", encoding="utf-8")

    component = KreuzbergFileLoaderComponent()
    payload = component.build(file_path=str(source_file))

    assert payload["bytes"] == b"hello from path"
    assert payload["filename"] == "sample.txt"
    assert payload["mime"] == "text/plain"
    assert payload["source_uri"] == str(source_file)


def test_file_loader_supports_in_memory_upload() -> None:
    upload = BytesIO(b"in memory content")
    upload.name = "memo.md"  # type: ignore[attr-defined]

    component = KreuzbergFileLoaderComponent()
    payload = component.build(file=upload)

    assert payload["bytes"] == b"in memory content"
    assert payload["filename"] == "memo.md"
    assert payload["mime"] == "text/markdown"


def test_file_loader_uses_unknown_filename_when_missing() -> None:
    component = KreuzbergFileLoaderComponent()

    payload = component.build(file=b"raw-bytes")

    assert payload["filename"] == "unknown"
    assert payload["mime"] == "application/octet-stream"


def test_file_loader_source_id_is_deterministic() -> None:
    component = KreuzbergFileLoaderComponent()

    first = component.build(file=b"same", filename_override="a.txt")
    second = component.build(file=b"same", filename_override="a.txt")

    assert first["source_id"] == second["source_id"]


def test_file_loader_requires_file_or_file_path() -> None:
    component = KreuzbergFileLoaderComponent()

    with pytest.raises(ValueError, match="requires either 'file' or 'file_path'"):
        component.build()
