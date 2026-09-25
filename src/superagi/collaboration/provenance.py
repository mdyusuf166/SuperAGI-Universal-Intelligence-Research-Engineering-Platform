"""Provenance references. Missing sources stay missing."""

from __future__ import annotations

from uuid import UUID

from superagi.memory.evidence.provenance import ProvenanceRecord, ProvenanceStage

from .models import ProvenanceRef


class ProvenanceLog:
    def __init__(self) -> None:
        self.refs: list[ProvenanceRef] = []

    def record(self, *, source: str | None, originating_agent: str, session_id: UUID | None = None, evidence: list[str] | None = None, related_task: str | None = None, related_decision: str | None = None, memory=None) -> ProvenanceRef | None:
        if not source:
            return None
        ref = ProvenanceRef(source=source, evidence=list(evidence or []), originating_agent=originating_agent, session_id=session_id, related_task=related_task, related_decision=related_decision)
        self.refs.append(ref)
        if memory is not None:
            memory.provenance.add(ProvenanceRecord(stage=ProvenanceStage.AGENT_RESULT, producer=originating_agent, source=source, operation="collaboration_record", output_references=(str(ref.id),), metadata={"session_id": str(session_id) if session_id else ""}))
        return ref
