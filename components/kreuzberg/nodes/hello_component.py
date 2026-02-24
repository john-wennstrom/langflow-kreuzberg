"""Minimal Kreuzberg component used to validate package registration."""

from __future__ import annotations

from lfx.custom.custom_component.component import Component
from lfx.io import Output, StrInput
from lfx.schema import Data


class KreuzbergHelloComponent(Component):
    """Return a deterministic greeting payload for Langflow node smoke tests."""

    display_name = "Kreuzberg Hello"
    description = "Returns a deterministic greeting for registration checks."
    documentation = "https://github.com/kreuzberg-ai/langflow-kreuzberg"
    icon = "message-circle"
    name = "KreuzbergHello"

    inputs = [StrInput(name="name", display_name="Name", value="world")]
    outputs = [Output(name="greeting", display_name="Greeting", method="build_greeting")]

    _last_greeting: dict[str, str] | None = None

    def build(self, name: str = "world") -> dict[str, str]:
        """Return a deterministic greeting payload."""
        greeting = {"message": f"Hello, {name}!"}
        self._last_greeting = greeting
        self.status = greeting["message"]
        return greeting

    def build_greeting(self) -> Data:
        if self._last_greeting is None:
            raise ValueError("No greeting has been generated yet.")
        return Data(data=self._last_greeting)
