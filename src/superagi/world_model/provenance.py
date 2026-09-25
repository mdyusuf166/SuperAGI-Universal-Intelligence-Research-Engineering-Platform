"""Provenance links. A missing source stays missing."""

from __future__ import annotations

from superagi.memory.evidence.provenance import ProvenanceRecord, ProvenanceStage

from .models import ProvenanceRef, ProvenanceStatus


def provenance_from(source: str | None, *, evidence: list[str] | None = None, agent: str | None = None) -> ProvenanceRef:
    cleaned = source.strip() if isinstance(source, str) else ""
    return ProvenanceRef(source=cleaned or None, agent=agent, evidence_refs=list(evidence or []), status=ProvenanceStatus.PRESENT if cleaned else ProvenanceStatus.MISSING)


class ProvenanceLog:
    def record(self, *, source: str | None, agent: str | None = None, evidence: list[str] | None = None, memory=None) -> ProvenanceRef:
        link = provenance_from(source, evidence=evidence, agent=agent)
        if memory is not None and link.status == ProvenanceStatus.PRESENT:
            memory.provenance.add(ProvenanceRecord(stage=ProvenanceStage.AGENT_RESULT, producer=agent or "world_model", source=link.source or "", operation="world_model_record", input_references=tuple(evidence or []), output_references=(str(link.id),)))
        return link
