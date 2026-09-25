"""One-call cycle runner."""

from __future__ import annotations

from .loop import CognitiveCycle
from .models import CognitiveState, CycleRequest


class CognitivePipeline:
    def run(self, request: CycleRequest, *, memory=None, graph=None, event_bus=None, simulation_backend=None) -> CognitiveState:
        return CognitiveCycle(memory=memory, graph=graph, event_bus=event_bus, simulation_backend=simulation_backend).run(request)
