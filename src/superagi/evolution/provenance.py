"""Provenance links. A missing source stays missing."""

from __future__ import annotations

from superagi.memory.evidence.provenance import ProvenanceRecord, ProvenanceStage

from .models import ProvenanceLink


class ProvenanceLog:
    def record(self, *, source: str | None, agent: str | None = None, task: str | None = None, evidence: list[str] | None = None, simulation_id: str | None = None, prediction_id: str | None = None, plan_id: str | None = None, decision_id: str | None = None, proposal_id: str | None = None, memory=None) -> ProvenanceLink:
        missing = not source
        link = ProvenanceLink(source=source, agent=agent, task=task, evidence=list(evidence or []), simulation_id=simulation_id, prediction_id=prediction_id, plan_id=plan_id, decision_id=decision_id, proposal_id=proposal_id, missing=missing)
        if memory is not None and source:
            memory.provenance.add(ProvenanceRecord(stage=ProvenanceStage.AGENT_RESULT, producer=agent or "evolution", source=source, operation="evolution_record", input_references=tuple(evidence or []), output_references=(str(link.id),)))
        return link
