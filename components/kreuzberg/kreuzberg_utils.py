"""Utility helpers shared across Kreuzberg components."""

from __future__ import annotations

from collections.abc import Iterable


def normalize_to_list(data_or_list: object) -> list[object]:
    """Normalize a single item or iterable into a list."""
    if data_or_list is None:
        return []
    if isinstance(data_or_list, list):
        return data_or_list
    if isinstance(data_or_list, Iterable) and not isinstance(data_or_list, (str, bytes, dict)):
        return list(data_or_list)
    return [data_or_list]
