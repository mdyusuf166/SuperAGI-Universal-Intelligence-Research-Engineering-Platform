"""Cycle provenance. A missing source stays missing."""

from __future__ import annotations

from .models import CycleProvenance, ProvenanceNote


def _note(source: str | None, ref: str = "") -> ProvenanceNote:
    cleaned = source.strip() if isinstance(source, str) else ""
    return ProvenanceNote(source=cleaned or None, status="PRESENT" if cleaned else "MISSING", ref_id=ref)


def cycle_provenance(source: str | None, *, task_id: str, cycle_id: str) -> CycleProvenance:
    return CycleProvenance(
        cycle=_note(source, cycle_id),
        task=_note(source, task_id),
        observation=_note(source),
        memory=_note(source),
        evidence=_note(source),
        world_model=_note(source),
        reasoning=_note(source),
        simulation=_note(source),
        prediction=_note(source),
        plan=_note(source),
        decision=_note(source),
        action_proposal=_note(source),
        evaluation=_note(source),
        learning_proposal=_note(source),
        evolution_proposal=_note(source),
    )
