"""Shared typing primitives for Kreuzberg components."""

from typing import Any, TypedDict


class DocumentSource(TypedDict, total=False):
    """Canonical input shape for loader outputs."""

    bytes: bytes
    path: str
    url: str
    filename: str
    mime: str
    source_id: str
    source_uri: str | None


class ExtractedDocument(TypedDict, total=False):
    """Canonical extraction output payload."""

    text: str
    metadata: dict[str, Any]
    tables: list[dict[str, Any]] | None
    images: list[dict[str, Any]] | None
    pages: list[dict[str, Any]] | None


class Chunk(TypedDict, total=False):
    """Canonical chunk payload."""

    id: str
    text: str
    metadata: dict[str, Any]
    page: int | None
    offset_start: int | None
    offset_end: int | None


class ComponentPayload(TypedDict, total=False):
    """Generic payload type used by minimal components."""

    message: str
