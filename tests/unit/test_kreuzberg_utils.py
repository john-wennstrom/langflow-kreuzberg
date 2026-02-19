"""Unit tests for Kreuzberg shared utility helpers."""

from dataclasses import dataclass

import pytest

from components.kreuzberg.kreuzberg_utils import (
    ensure_metadata_dict,
    hash_id,
    merge_metadata,
    normalize_to_list,
)


@dataclass
class DummyData:
    data: dict


def test_hash_id_is_deterministic() -> None:
    first = hash_id("source", "file.pdf", 123)
    second = hash_id("source", "file.pdf", 123)

    assert first == second
    assert len(first) == 32


def test_normalize_to_list_supports_single_and_iterable() -> None:
    assert normalize_to_list("value") == ["value"]
    assert normalize_to_list(("a", "b")) == ["a", "b"]
    assert normalize_to_list(None) == []


def test_ensure_metadata_dict_handles_dict_payload() -> None:
    payload = {"metadata": {"source_id": "abc"}}

    assert ensure_metadata_dict(payload) == {"source_id": "abc"}


def test_ensure_metadata_dict_handles_data_object_and_missing_metadata() -> None:
    assert ensure_metadata_dict(DummyData(data={"metadata": {"page": 2}})) == {"page": 2}
    assert ensure_metadata_dict(DummyData(data={"text": "hi"})) == {}


def test_merge_metadata_overwrite_policy() -> None:
    merged = merge_metadata({"a": 1, "b": 2}, {"b": 3, "c": 4}, policy="overwrite")

    assert merged == {"a": 1, "b": 3, "c": 4}


def test_merge_metadata_keep_policy() -> None:
    merged = merge_metadata({"a": 1, "b": 2}, {"b": 3, "c": 4}, policy="keep")

    assert merged == {"a": 1, "b": 2, "c": 4}


def test_merge_metadata_raise_policy_conflict() -> None:
    with pytest.raises(ValueError, match="metadata conflict"):
        merge_metadata({"a": 1}, {"a": 2}, policy="raise")


def test_merge_metadata_invalid_policy() -> None:
    with pytest.raises(ValueError, match="policy must be one"):
        merge_metadata({"a": 1}, {"b": 2}, policy="invalid")
