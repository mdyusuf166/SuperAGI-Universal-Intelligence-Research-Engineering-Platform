"""In-memory timeline. This is not a temporal database."""

from __future__ import annotations

from uuid import UUID

from .models import EpistemicStatus, TemporalLink, TemporalOrder, TimeInterval, TransitionKind, WorldSnapshot, WorldTransition


class Timeline:
    def __init__(self) -> None:
        self._snapshots: list[WorldSnapshot] = []
        self._transitions: list[WorldTransition] = []
        self._links: list[TemporalLink] = []

    def add_snapshot(self, snapshot: WorldSnapshot) -> WorldSnapshot:
        self._snapshots.append(snapshot)
        return snapshot

    def add_transition(self, transition: WorldTransition) -> WorldTransition:
        previous = self._require(transition.previous_id)
        nxt = self._require(transition.next_id)
        if nxt.epistemic == EpistemicStatus.SIMULATED and transition.kind != TransitionKind.SIMULATED_TRANSITION:
            raise ValueError("Simulated state requires SIMULATED_TRANSITION")
        if nxt.epistemic == EpistemicStatus.PREDICTED and transition.kind != TransitionKind.PREDICTED_TRANSITION:
            raise ValueError("Predicted state requires PREDICTED_TRANSITION")
        if nxt.epistemic == EpistemicStatus.OBSERVED and transition.kind != TransitionKind.OBSERVED_TRANSITION:
            raise ValueError("Observed state requires OBSERVED_TRANSITION")
        if previous.epistemic == EpistemicStatus.OBSERVED and nxt.epistemic == EpistemicStatus.SIMULATED and transition.kind != TransitionKind.SIMULATED_TRANSITION:
            raise ValueError("Observed and simulated states cannot share an unlabeled transition")
        self._transitions.append(transition)
        self._links.append(TemporalLink(earlier_step=previous.time.step, later_step=nxt.time.step, order=self.order(previous.time.step, nxt.time.step)))
        return transition

    def snapshots(self) -> list[WorldSnapshot]:
        return list(self._snapshots)

    def transitions(self) -> list[WorldTransition]:
        return list(self._transitions)

    def state_at(self, step: int) -> WorldSnapshot | None:
        eligible = [(index, item) for index, item in enumerate(self._snapshots) if item.time.step <= step]
        if not eligible:
            return None
        eligible.sort(key=lambda pair: (pair[1].time.step, pair[0]))
        return eligible[-1][1]

    def order(self, left: int, right: int) -> TemporalOrder:
        if left < right:
            return TemporalOrder.BEFORE
        if left > right:
            return TemporalOrder.AFTER
        return TemporalOrder.DURING

    def intervals(self, left: TimeInterval, right: TimeInterval) -> TemporalOrder:
        if left.end < right.start:
            return TemporalOrder.BEFORE
        if right.end < left.start:
            return TemporalOrder.AFTER
        if (left.start <= right.start and left.end >= right.end) or (right.start <= left.start and right.end >= left.end):
            return TemporalOrder.DURING
        return TemporalOrder.OVERLAP

    def _require(self, snapshot_id: UUID) -> WorldSnapshot:
        for snapshot in self._snapshots:
            if snapshot.id == snapshot_id:
                return snapshot
        raise ValueError("Invalid snapshot reference")
