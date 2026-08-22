"""Optional LangGraph adapter placeholder.

The upstream project remains isolated under ``third_party/agents``. This module
will translate SuperAGI workflow requests to an upstream-compatible boundary
without importing upstream implementation details into the core package.
"""

from __future__ import annotations

from typing import Any

from superagi.integrations.base import IntegrationAdapter


class LangGraphAdapter(IntegrationAdapter):
    """Expose LangGraph availability without coupling SuperAGI to its internals."""

    def is_available(self) -> bool:
        try:
            import langgraph  # noqa: F401
        except ImportError:
            return False
        return True

    def capabilities(self) -> tuple[str, ...]:
        return ("stateful_workflows", "graph_execution", "checkpointing")

    def build_workflow(self, definition: dict[str, Any]) -> Any:
        """Build a workflow through a future translation layer."""
        raise NotImplementedError("LangGraph workflow translation is not implemented yet")
