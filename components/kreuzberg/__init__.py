"""Kreuzberg Langflow component bundle exports."""

from components.kreuzberg.kreuzberg_types import (
    Chunk,
    ComponentPayload,
    DocumentSource,
    ExtractedDocument,
)
from components.kreuzberg.kreuzberg_utils import (
    ensure_metadata_dict,
    hash_id,
    merge_metadata,
    normalize_to_list,
)
from components.kreuzberg.nodes.hello_component import KreuzbergHelloComponent

__all__ = [
    "Chunk",
    "ComponentPayload",
    "DocumentSource",
    "ExtractedDocument",
    "KreuzbergHelloComponent",
    "ensure_metadata_dict",
    "hash_id",
    "merge_metadata",
    "normalize_to_list",
]

COMPONENT_REGISTRY = {
    "KreuzbergHello": KreuzbergHelloComponent,
}
