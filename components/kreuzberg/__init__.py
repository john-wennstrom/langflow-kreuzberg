"""Kreuzberg Langflow component bundle exports."""

from components.kreuzberg.kreuzberg_types import ComponentPayload, DocumentSource
from components.kreuzberg.kreuzberg_utils import normalize_to_list
from components.kreuzberg.nodes.hello_component import KreuzbergHelloComponent

__all__ = [
    "ComponentPayload",
    "DocumentSource",
    "KreuzbergHelloComponent",
    "normalize_to_list",
]

COMPONENT_REGISTRY = {
    "KreuzbergHello": KreuzbergHelloComponent,
}
