"""Stable contracts for optional upstream integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IntegrationAdapter(ABC):
    """Common lifecycle contract for an isolated upstream adapter."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return whether the optional upstream dependency is installed and usable."""

    @abstractmethod
    def capabilities(self) -> tuple[str, ...]:
        """Return capability names exposed by this adapter."""


class OptionalIntegrationAdapter(IntegrationAdapter):
    """Dependency-free boundary used until an integration is implemented."""

    def __init__(self, name: str, capability_names: tuple[str, ...] = ()) -> None:
        self.name = name
        self._capability_names = capability_names

    def is_available(self) -> bool:
        return False

    def capabilities(self) -> tuple[str, ...]:
        return self._capability_names

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"


class ResearchEngineAdapter(IntegrationAdapter):
    """Contract for research systems without exposing their internal APIs."""

    @abstractmethod
    def search(self, query: str, **options: Any) -> list[dict[str, Any]]:
        """Search for relevant sources or experiments."""

    @abstractmethod
    def retrieve(self, reference: str, **options: Any) -> dict[str, Any]:
        """Retrieve a source or experiment by reference."""

    @abstractmethod
    def analyze(self, evidence: list[dict[str, Any]], **options: Any) -> dict[str, Any]:
        """Analyze collected evidence."""

    @abstractmethod
    def synthesize(self, analysis: dict[str, Any], **options: Any) -> dict[str, Any]:
        """Synthesize an explicit, traceable result."""
