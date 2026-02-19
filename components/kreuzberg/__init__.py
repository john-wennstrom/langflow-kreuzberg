"""Kreuzberg Langflow component bundle exports."""

from components.kreuzberg.kreuzberg_cache import (
    CacheBackend,
    FilesystemCacheBackend,
    RunReport,
    build_cache_key,
    log_run_report,
    parallel_map,
)
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
    "CacheBackend",
    "Chunk",
    "FilesystemCacheBackend",
    "ComponentPayload",
    "DocumentSource",
    "ExtractedDocument",
    "KreuzbergHelloComponent",
    "RunReport",
    "build_cache_key",
    "ensure_metadata_dict",
    "hash_id",
    "log_run_report",
    "merge_metadata",
    "parallel_map",
    "normalize_to_list",
]

COMPONENT_REGISTRY = {
    "KreuzbergHello": KreuzbergHelloComponent,
}
