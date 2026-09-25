"""State transitions that keep observed, simulated, and predicted labels apart."""

from __future__ import annotations

from .models import EntityState, EpistemicStatus, TimePoint, TransitionKind, WorldSnapshot, WorldState, WorldTransition
from .provenance import provenance_from
from .temporal import Timeline


def _state_for(entity_id, properties, epistemic, step: int, source: str | None) -> WorldState:
    return WorldState(
        label=f"step-{step}",
        epistemic=epistemic,
        provenance=provenance_from(source, agent="state_updater"),
        entity_states=[EntityState(entity_id=entity_id, properties=list(properties), epistemic=epistemic, time=TimePoint(step=step, label=f"t{step}"), provenance=provenance_from(source, agent="state_updater"))],
    )


def snapshot_for(entity_id, properties, epistemic: EpistemicStatus, step: int, source: str | None) -> WorldSnapshot:
    return WorldSnapshot(time=TimePoint(step=step, label=f"t{step}"), state=_state_for(entity_id, properties, epistemic, step, source), epistemic=epistemic, provenance=provenance_from(source, agent="state_updater"))


def record_transition(timeline: Timeline, *, previous: WorldSnapshot, nxt: WorldSnapshot, kind: TransitionKind, action_name: str = "", event_id=None, observations=None, prediction_method: str | None = None, simulation_classification: str | None = None, source: str | None = None) -> WorldTransition:
    known = {item.id for item in timeline.snapshots()}
    if previous.id not in known:
        timeline.add_snapshot(previous)
    if nxt.id not in known and nxt.id != previous.id:
        timeline.add_snapshot(nxt)
    transition = WorldTransition(kind=kind, previous_id=previous.id, next_id=nxt.id, event_id=event_id, action_name=action_name, observations=list(observations or []), prediction_method=prediction_method, simulation_classification=simulation_classification, provenance=provenance_from(source, agent="state_updater"))
    return timeline.add_transition(transition)
