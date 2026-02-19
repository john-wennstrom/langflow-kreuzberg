"""Kreuzberg Langflow component bundle exports."""

from components.kreuzberg.kreuzberg_cache import (
    CacheBackend,
    FilesystemCacheBackend,
    RunReport,
    build_cache_key,
    log_run_report,
    parallel_map,
)
from components.kreuzberg.kreuzberg_errors import (
    CorruptDocumentError,
    ExtractionTimeoutError,
    KreuzbergComponentError,
    OCRBackendMissingError,
    RemoteExtractionError,
    UnsupportedFormatError,
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
from components.kreuzberg.nodes.extract import KreuzbergExtractComponent
from components.kreuzberg.nodes.file_loader import KreuzbergFileLoaderComponent
from components.kreuzberg.nodes.hello_component import KreuzbergHelloComponent

__all__ = [
    "CacheBackend",
    "Chunk",
    "FilesystemCacheBackend",
    "ComponentPayload",
    "CorruptDocumentError",
    "DocumentSource",
    "ExtractionTimeoutError",
    "ExtractedDocument",
    "KreuzbergExtractComponent",
    "KreuzbergFileLoaderComponent",
    "KreuzbergComponentError",
    "KreuzbergHelloComponent",
    "OCRBackendMissingError",
    "RemoteExtractionError",
    "RunReport",
    "build_cache_key",
    "ensure_metadata_dict",
    "hash_id",
    "log_run_report",
    "merge_metadata",
    "parallel_map",
    "UnsupportedFormatError",
    "normalize_to_list",
]

COMPONENT_REGISTRY = {
    "KreuzbergHello": KreuzbergHelloComponent,
    "KreuzbergFileLoader": KreuzbergFileLoaderComponent,
    "KreuzbergExtract": KreuzbergExtractComponent,
}
