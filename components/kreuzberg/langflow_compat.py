"""Compatibility shims for running Kreuzberg components with/without Langflow installed."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:  # pragma: no cover - exercised when Langflow is installed
    from langflow.custom import Component  # type: ignore
    from langflow.io import (  # type: ignore
        BoolInput,
        DataInput,
        DropdownInput,
        MessageTextInput,
        Output,
    )
    from langflow.schema import Data  # type: ignore
except Exception:  # pragma: no cover - local fallback for tests

    class Component:  # noqa: D401
        """Fallback Component base class used in tests when Langflow is unavailable."""

    @dataclass(frozen=True)
    class _BaseInput:
        name: str
        display_name: str
        info: str = ""
        value: Any = None
        advanced: bool = False
        options: list[str] | None = None
        is_list: bool = False

    class DataInput(_BaseInput):
        pass

    class MessageTextInput(_BaseInput):
        pass

    class BoolInput(_BaseInput):
        pass

    class DropdownInput(_BaseInput):
        pass

    @dataclass(frozen=True)
    class Output:
        name: str
        display_name: str
        method: str

    @dataclass
    class Data:
        data: dict[str, Any]
