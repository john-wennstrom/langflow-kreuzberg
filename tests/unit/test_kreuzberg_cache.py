"""Unit tests for Kreuzberg caching and concurrency helpers."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from components.kreuzberg.kreuzberg_cache import (
    FilesystemCacheBackend,
    build_cache_key,
    log_run_report,
    parallel_map,
)


def multiply_by_two(value: int) -> int:
    return value * 2


def test_filesystem_cache_backend_roundtrip(tmp_path: Path) -> None:
    backend = FilesystemCacheBackend(cache_dir=tmp_path)
    key = backend.make_cache_key("extract", "doc-a", 1)

    assert backend.get(key) is None

    backend.set(key, b"payload")

    assert backend.get(key) == b"payload"


def test_filesystem_cache_backend_disable_cache(tmp_path: Path) -> None:
    backend = FilesystemCacheBackend(cache_dir=tmp_path, disable_cache=True)
    key = backend.make_cache_key("extract", "doc-b")

    backend.set(key, b"payload")

    assert backend.get(key) is None


def test_build_cache_key_is_deterministic() -> None:
    first = build_cache_key("embed", "chunk-1", 42)
    second = build_cache_key("embed", "chunk-1", 42)

    assert first == second
    assert len(first) == 32


def test_parallel_map_thread_mode_preserves_order() -> None:
    result = parallel_map(multiply_by_two, [5, 1, 3], max_workers=2, mode="thread")

    assert result == [10, 2, 6]


def test_parallel_map_process_mode_preserves_order() -> None:
    result = parallel_map(multiply_by_two, [2, 4, 6], max_workers=2, mode="process")

    assert result == [4, 8, 12]


def test_parallel_map_invalid_arguments() -> None:
    with pytest.raises(ValueError, match="max_workers"):
        parallel_map(multiply_by_two, [1], max_workers=0)

    with pytest.raises(ValueError, match="mode"):
        parallel_map(multiply_by_two, [1], max_workers=1, mode="invalid")  # type: ignore[arg-type]


def test_log_run_report_emits_expected_message(caplog: pytest.LogCaptureFixture) -> None:
    report = {
        "duration_ms": 12,
        "cache_hits": 3,
        "cache_misses": 1,
        "errors": 0,
        "item_count": 4,
    }

    logger = logging.getLogger("kreuzberg-tests")
    with caplog.at_level(logging.INFO, logger="kreuzberg-tests"):
        log_run_report(logger, "BatchExtract", report)

    assert "BatchExtract run_report duration_ms=12 cache_hits=3" in caplog.text
