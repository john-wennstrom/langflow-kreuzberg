"""Utility helpers shared across Kreuzberg components."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from hashlib import sha256
from typing import Any


def normalize_to_list(data_or_list: object) -> list[object]:
    """Normalize a single item or iterable into a list."""
    if data_or_list is None:
        return []
    if isinstance(data_or_list, list):
        return data_or_list
    if isinstance(data_or_list, Iterable) and not isinstance(data_or_list, (str, bytes, dict)):
        return list(data_or_list)
    return [data_or_list]


def ensure_metadata_dict(data: object) -> dict[str, Any]:
    """Return a metadata dictionary from a Langflow-like payload.

    Supports either a plain dictionary payload or objects with a ``data`` attribute
    (matching Langflow's ``Data`` object shape).
    """

    payload: object = data
    if hasattr(data, "data"):
        payload = data.data

    if not isinstance(payload, dict):
        return {}

    metadata = payload.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def hash_id(*parts: object) -> str:
    """Build a deterministic 32-character SHA256 identifier from parts."""

    serialized_parts = [str(part) for part in parts]
    digest = sha256("||".join(serialized_parts).encode("utf-8")).hexdigest()
    return digest[:32]


def merge_metadata(
    base: Mapping[str, Any] | None,
    extra: Mapping[str, Any] | None,
    policy: str = "overwrite",
) -> dict[str, Any]:
    """Merge two metadata mappings using a conflict policy.

    Policies:
    - ``overwrite``: values in ``extra`` replace values from ``base``
    - ``keep``: values in ``base`` are preserved when key conflicts
    - ``raise``: raise ``ValueError`` when conflicting values differ
    """

    if policy not in {"overwrite", "keep", "raise"}:
        raise ValueError("policy must be one of: overwrite, keep, raise")

    merged: dict[str, Any] = dict(base or {})
    for key, value in dict(extra or {}).items():
        if key not in merged:
            merged[key] = value
            continue

        if policy == "overwrite":
            merged[key] = value
        elif policy == "keep":
            continue
        elif merged[key] != value:
            raise ValueError(f"metadata conflict for key '{key}'")

    return merged
