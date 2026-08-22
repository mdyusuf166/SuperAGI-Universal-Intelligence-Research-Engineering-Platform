from __future__ import annotations

from uuid import UUID

from .events import EventBus
from .models import Event


class ExecutionTrace:
    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def events_for_task(self, task_id: UUID) -> list[Event]:
        return self.event_bus.events(task_id)

    def event_types_for_task(self, task_id: UUID) -> list[str]:
        return [event.event_type.value for event in self.events_for_task(task_id)]
