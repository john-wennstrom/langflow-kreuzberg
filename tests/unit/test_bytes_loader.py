"""Tests for the Kreuzberg bytes loader component."""

from __future__ import annotations

import base64

import pytest

from components.kreuzberg.nodes.bytes_loader import KreuzbergBytesLoaderComponent


def test_bytes_loader_decodes_valid_base64() -> None:
    component = KreuzbergBytesLoaderComponent()
    encoded = base64.b64encode(b"hello bytes").decode("ascii")

    payload = component.build(data_input=encoded, input_format="base64", filename="hello.txt")

    assert payload["bytes"] == b"hello bytes"
    assert payload["filename"] == "hello.txt"
    assert payload["mime"] == "text/plain"


def test_bytes_loader_invalid_base64_has_actionable_error() -> None:
    component = KreuzbergBytesLoaderComponent()

    with pytest.raises(ValueError, match="Invalid base64 input"):
        component.build(
            data_input="definitely not base64!",
            input_format="base64",
            filename="x.bin",
        )


def test_bytes_loader_supports_raw_bytes_string() -> None:
    component = KreuzbergBytesLoaderComponent()

    payload = component.build(
        data_input="plain-text",
        input_format="bytes_str",
        filename="payload.md",
    )

    assert payload["bytes"] == b"plain-text"
    assert payload["mime"] == "text/markdown"


def test_bytes_loader_source_id_is_deterministic() -> None:
    component = KreuzbergBytesLoaderComponent()

    first = component.build(data_input="repeat", input_format="bytes_str", filename="same.txt")
    second = component.build(data_input="repeat", input_format="bytes_str", filename="same.txt")

    assert first["source_id"] == second["source_id"]
