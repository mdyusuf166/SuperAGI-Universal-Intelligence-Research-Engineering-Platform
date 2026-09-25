"""Evolution proposals. This cycle never edits source code or deploys anything."""

from __future__ import annotations

from superagi.collaboration.decisions import DecisionSupport

from .evaluation import EvolutionReview, MetaEvaluator
from .models import CapabilityGap, EvolutionLifecycle, EvolutionProposal, ProposedChange, ProvenanceLink
from .safety import EvolutionSafetyPolicy


_CHANGES = {
    "simulation_backend_unavailable": ("new domain adapter", "Describe a future adapter boundary without enabling a backend."),
    "prediction_uncertainty": ("new evaluation", "Add a holdout check before treating a forecast as evidence."),
    "planning_failure": ("new planner strategy", "Ask for a smaller goal decomposition with explicit preconditions."),
    "evidence_gap": ("new memory strategy", "Ask the user for a source before storing a claim."),
    "tool_gap": ("new tool", "Describe a tool interface. Do not install or execute it."),
}


class EvolutionCycle:
    def __init__(self) -> None:
        self.safety = EvolutionSafetyPolicy()
        self.reviewer = EvolutionReview()
        self.evaluator = MetaEvaluator()

    def propose(self, gap: CapabilityGap, *, approved: bool = False, source: str | None = None) -> EvolutionProposal:
        safety = self.safety.assess(f"{gap.statement} {gap.code}")
        if not safety["allowed"]:
            raise PermissionError("Safety policy rejected the evolution request")
        kind, statement = _CHANGES.get(gap.code, ("new skill", "Describe the missing capability. Do not apply a change automatically."))
        provenance = ProvenanceLink(source=source, agent="evolution_cycle", missing=not source)
        proposal = EvolutionProposal(
            gap=gap,
            target=gap.code,
            change=ProposedChange(kind=kind, statement=statement),
            expected_benefit="The gap would be documented for a human to review.",
            risks=["The proposal may be unnecessary.", "No measured improvement exists."],
            validation_requirement="A human checks the proposal against the recorded gap.",
            rollback_requirement="No change is applied, so rollback is to leave the source tree untouched.",
            human_approval=approved,
            lifecycle=EvolutionLifecycle.PROPOSAL if approved else EvolutionLifecycle.AWAITING_HUMAN_APPROVAL,
            states_visited=[
                EvolutionLifecycle.OBSERVE,
                EvolutionLifecycle.EVALUATE,
                EvolutionLifecycle.IDENTIFY_GAP,
                EvolutionLifecycle.PROPOSE_IMPROVEMENT,
                EvolutionLifecycle.SIMULATE,
                EvolutionLifecycle.VERIFY,
                EvolutionLifecycle.REQUEST_HUMAN_APPROVAL,
                EvolutionLifecycle.PROPOSAL if approved else EvolutionLifecycle.AWAITING_HUMAN_APPROVAL,
            ],
            applied=False,
            limitations=["PROPOSAL_ONLY. Source code, permissions, deployment, and external systems were not changed."],
            provenance=provenance,
        )
        decision = DecisionSupport().prepare(question=f"Approve evolution proposal {gap.code}?", options=[{"name": "hold", "criteria": {"risk": 1}, "evidence": [gap.statement], "assumptions": ["No change should be applied in ARC-15."]}], criteria=["risk"], evidence=[gap.statement], assumptions=["Human approval does not execute the change."], risks=proposal.risks, tradeoffs="Holding avoids an unvalidated change.")
        if approved:
            DecisionSupport().approve(decision["decision"], human=True)
        proposal.provenance.decision_id = str(decision["decision"].id) if proposal.provenance else None
        return proposal

    def apply(self, proposal: EvolutionProposal) -> EvolutionProposal:
        raise PermissionError("ARC-15 does not apply evolution proposals, even after human approval")
