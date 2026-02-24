"""Tests for the minimal Kreuzberg component scaffold."""

from components.kreuzberg import (
    COMPONENT_REGISTRY,
    KreuzbergExtractComponent,
    KreuzbergFileLoaderComponent,
    KreuzbergHelloComponent,
    normalize_to_list,
)


def test_hello_component_build_returns_deterministic_message() -> None:
    component = KreuzbergHelloComponent()

    result = component.build(name="Kreuzberg")

    assert result == {"message": "Hello, Kreuzberg!"}


def test_component_registry_contains_hello_component() -> None:
    assert COMPONENT_REGISTRY["KreuzbergHello"] is KreuzbergHelloComponent


def test_normalize_to_list_handles_single_and_list_values() -> None:
    assert normalize_to_list("text") == ["text"]
    assert normalize_to_list(["a", "b"]) == ["a", "b"]
    assert normalize_to_list(None) == []


def test_component_registry_contains_file_loader_component() -> None:
    assert COMPONENT_REGISTRY["KreuzbergFileLoader"] is KreuzbergFileLoaderComponent


def test_component_registry_contains_extract_component() -> None:
    assert COMPONENT_REGISTRY["KreuzbergExtract"] is KreuzbergExtractComponent


def test_registry_components_define_langflow_node_ports() -> None:
    hello = KreuzbergHelloComponent()
    file_loader = KreuzbergFileLoaderComponent()

    assert any(port.name == "name" for port in hello.inputs)
    assert any(port.name == "greeting" for port in hello.outputs)
    assert any(port.name == "file" for port in file_loader.inputs)
    assert any(port.name == "document_source" for port in file_loader.outputs)
