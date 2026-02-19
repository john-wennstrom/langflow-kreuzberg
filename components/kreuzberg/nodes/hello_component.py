"""Minimal Kreuzberg component used to validate package registration."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HelloOutput:
    """Structured output payload for the hello component."""

    message: str


class KreuzbergHelloComponent:
    """A tiny component used to verify bundle discovery and test wiring."""

    display_name = "Kreuzberg Hello"
    description = "Returns a deterministic greeting for registration checks."
    icon = "message-circle"
    name = "KreuzbergHello"

    def build(self, name: str = "world") -> dict[str, Any]:
        """Return a deterministic greeting payload."""
        return {"message": f"Hello, {name}!"}
