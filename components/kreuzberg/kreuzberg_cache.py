"""Caching and concurrency utilities shared by Kreuzberg components."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Literal, Protocol, TypedDict, TypeVar

from components.kreuzberg.kreuzberg_utils import hash_id

T = TypeVar("T")
R = TypeVar("R")


class RunReport(TypedDict):
    """Structured execution summary used across cache-enabled components."""

    duration_ms: int
    cache_hits: int
    cache_misses: int
    errors: int
    item_count: int


class CacheBackend(Protocol):
    """Common cache interface for Kreuzberg components."""

    def get(self, key: str) -> bytes | None:
        """Return bytes for a cache key or ``None`` when missing."""

    def set(self, key: str, value: bytes) -> None:
        """Persist bytes for a cache key."""


class FilesystemCacheBackend:
    """Filesystem-based cache backend with optional global disable flag."""

    def __init__(self, cache_dir: str | Path, disable_cache: bool = False) -> None:
        self.cache_dir = Path(cache_dir)
        self.disable_cache = disable_cache
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> bytes | None:
        if self.disable_cache:
            return None

        path = self._cache_path(key)
        if not path.exists() or not path.is_file():
            return None

        return path.read_bytes()

    def set(self, key: str, value: bytes) -> None:
        if self.disable_cache:
            return

        path = self._cache_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)

    def make_cache_key(self, component_name: str, *content_parts: object) -> str:
        """Build deterministic cache keys using the shared ``hash_id`` helper."""

        return hash_id(component_name, *content_parts)

    def _cache_path(self, key: str) -> Path:
        safe_key = "".join(char for char in key if char.isalnum() or char in {"-", "_"})
        return self.cache_dir / f"{safe_key}.bin"


def build_cache_key(component_name: str, *content_parts: object) -> str:
    """Build a deterministic cache key for any backend."""

    return hash_id(component_name, *content_parts)


def parallel_map(
    fn: Callable[[T], R],
    items: list[T],
    max_workers: int,
    mode: Literal["thread", "process"] = "thread",
) -> list[R]:
    """Map ``fn`` across items with optional thread/process execution.

    Ordering always matches the original ``items`` ordering.
    """

    if max_workers < 1:
        raise ValueError("max_workers must be >= 1")
    if mode not in {"thread", "process"}:
        raise ValueError("mode must be either 'thread' or 'process'")
    if not items:
        return []

    executor_type = ThreadPoolExecutor if mode == "thread" else ProcessPoolExecutor
    with executor_type(max_workers=max_workers) as executor:
        return list(executor.map(fn, items))


def log_run_report(logger: Any, component_name: str, run_report: RunReport) -> None:
    """Emit a run report to a logger in a consistent format."""

    logger.info(
        "%s run_report duration_ms=%s cache_hits=%s cache_misses=%s errors=%s item_count=%s",
        component_name,
        run_report["duration_ms"],
        run_report["cache_hits"],
        run_report["cache_misses"],
        run_report["errors"],
        run_report["item_count"],
    )
