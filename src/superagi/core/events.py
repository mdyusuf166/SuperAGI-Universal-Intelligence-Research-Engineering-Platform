from collections.abc import Callable

from .models import Event


class EventBus:
    def __init__(self) -> None:
        self._events: list[Event] = []
        self._subscribers: list[Callable[[Event], None]] = []

    def subscribe(self, handler: Callable[[Event], None]) -> None:
        self._subscribers.append(handler)

    def publish(self, event: Event) -> Event:
        self._events.append(event)
        for subscriber in tuple(self._subscribers):
            subscriber(event)
        return event

    def events(self, task_id=None) -> list[Event]:
        if task_id is None:
            return list(self._events)
        return [event for event in self._events if event.task_id == task_id]
