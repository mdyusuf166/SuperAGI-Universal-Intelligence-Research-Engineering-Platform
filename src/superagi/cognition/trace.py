"""Cognitive trace plus ARC-01 events. Chain-of-thought is not stored."""

from __future__ import annotations

from superagi.core.events import EventBus
from superagi.core.models import Event, EventType

from .models import CognitiveEventName, CognitiveEventRecord

_BUS = {
    CognitiveEventName.CYCLE_STARTED: EventType.TASK_STARTED,
    CognitiveEventName.OBSERVATION_INGESTED: EventType.TASK_STARTED,
    CognitiveEventName.CONTEXT_BUILT: EventType.MEMORY_RETRIEVED,
    CognitiveEventName.REASONING_COMPLETED: EventType.AGENT_COMPLETED,
    CognitiveEventName.SIMULATION_COMPLETED: EventType.TOOL_COMPLETED,
    CognitiveEventName.PREDICTION_COMPLETED: EventType.PREDICTION_COMPLETED,
    CognitiveEventName.PLAN_CREATED: EventType.PLAN_CREATED,
    CognitiveEventName.DECISION_PROPOSED: EventType.VERIFICATION_STARTED,
    CognitiveEventName.ACTION_PROPOSED: EventType.PLAN_CREATED,
    CognitiveEventName.SAFETY_REVIEWED: EventType.VERIFICATION_COMPLETED,
    CognitiveEventName.APPROVAL_REQUIRED: EventType.VERIFICATION_COMPLETED,
    CognitiveEventName.OBSERVATION_RECEIVED: EventType.TASK_STARTED,
    CognitiveEventName.EVALUATION_COMPLETED: EventType.VERIFICATION_COMPLETED,
    CognitiveEventName.LEARNING_PROPOSED: EventType.AGENT_COMPLETED,
    CognitiveEventName.EVOLUTION_PROPOSED: EventType.AGENT_COMPLETED,
    CognitiveEventName.CYCLE_COMPLETED: EventType.TASK_COMPLETED,
    CognitiveEventName.CYCLE_FAILED: EventType.TASK_FAILED,
}


class CognitiveTrace:
    def __init__(self, bus: EventBus | None, task_id) -> None:
        self.bus = bus
        self.task_id = task_id
        self.records: list[CognitiveEventRecord] = []

    def add(self, name: CognitiveEventName, summary: str) -> CognitiveEventRecord:
        record = CognitiveEventRecord(name=name, summary=summary[:180])
        self.records.append(record)
        if self.bus is not None:
            self.bus.publish(Event(event_type=_BUS[name], task_id=self.task_id, metadata={"cognitive_event": name.value, "summary": record.summary}))
        return record
