"""Integration checks for component registration."""

from __future__ import annotations

from components.kreuzberg import COMPONENT_REGISTRY
from components.kreuzberg.nodes.bytes_loader import KreuzbergBytesLoaderComponent


def test_bytes_loader_is_registered() -> None:
    assert COMPONENT_REGISTRY["KreuzbergBytesLoader"] is KreuzbergBytesLoaderComponent
