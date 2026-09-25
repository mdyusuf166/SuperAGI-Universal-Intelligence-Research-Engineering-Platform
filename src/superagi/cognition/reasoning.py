"""Structured reasoning artifacts. Inferences stay inferences."""

from __future__ import annotations

from .models import Claim, CognitiveContext, EpistemicStatus, ReasoningResult
from .uncertainty import lowest


class BoundedReasoner:
    def reason(self, *, goal: str, context: CognitiveContext, assumptions: list[str], research_note: str | None = None) -> ReasoningResult:
        claims: list[Claim] = []
        inferences: list[Claim] = []
        unknowns: list[str] = []
        contradictions: list[str] = []
        for item in context.evidence:
            claims.append(Claim(statement=item.label, epistemic=item.epistemic, evidence_refs=[item.ref_id] if item.ref_id else []))
            if item.epistemic == EpistemicStatus.CONTRADICTED:
                contradictions.append(item.label)
        for item in context.entities + context.relations:
            if item.epistemic == EpistemicStatus.CONTRADICTED:
                contradictions.append(item.label)
            elif item.epistemic == EpistemicStatus.UNKNOWN:
                unknowns.append(item.label)
            elif item.epistemic in {EpistemicStatus.OBSERVED, EpistemicStatus.EVIDENCED}:
                claims.append(Claim(statement=item.label, epistemic=item.epistemic, evidence_refs=[item.ref_id] if item.ref_id else []))
        if research_note:
            inferences.append(Claim(statement=research_note[:240], epistemic=EpistemicStatus.HYPOTHESIZED, evidence_refs=[]))
        if context.relations:
            inferences.append(Claim(statement="A recorded relation is present in the bounded context. The relation is not a truth guarantee.", epistemic=EpistemicStatus.INFERRED))
        if not claims and not research_note:
            unknowns.append("No evidenced claim was supplied for the goal.")
        confidences = [0.2] if research_note else []
        report = lowest(confidences)
        return ReasoningResult(claims=claims, inferences=inferences, unknowns=unknowns, contradictions=sorted(set(contradictions)), assumptions=list(assumptions), confidence=report.value, confidence_basis=report.basis, limitations=["Inferences are not facts.", "Hypotheses are not proof.", "No hidden chain-of-thought is stored."])
