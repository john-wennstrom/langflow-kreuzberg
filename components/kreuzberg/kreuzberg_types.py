"""Shared typing primitives for Kreuzberg components."""

from typing import TypedDict


class DocumentSource(TypedDict, total=False):
    """Canonical input shape for loader outputs."""

    bytes: bytes
    filename: str
    mime: str
    source_id: str
    source_uri: str | None


class ComponentPayload(TypedDict, total=False):
    """Generic payload type used by minimal components."""

    message: str
