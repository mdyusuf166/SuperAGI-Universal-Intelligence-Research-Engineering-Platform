"""Learning and evolution proposals. Neither one is applied."""

from __future__ import annotations

from superagi.evolution.evolution_cycle import EvolutionCycle
from superagi.evolution.models import CapabilityGap

from .models import CognitiveState, EvolutionRecord, LearningUpdateProposal


class LearningProposalService:
    def propose(self, state: CognitiveState) -> LearningUpdateProposal:
        if state.simulation_result and state.simulation_result.status == "SIMULATION_BACKEND_UNAVAILABLE":
            gap, statement = "simulation_backend_unavailable", "A simulation backend was requested and is unavailable."
        elif state.prediction_result and state.prediction_result.epistemic.value == "UNKNOWN":
            gap, statement = "prediction_uncertainty", "A forecast could not be formed from the supplied series."
        elif not state.evidence_refs:
            gap, statement = "evidence_gap", "The cycle has no evidence references."
        elif state.reasoning_result and state.reasoning_result.unknowns:
            gap, statement = "knowledge_gap", "The bounded context still contains unknown items."
        else:
            gap, statement = "capability_gap", "No measured gap was found. This note is still only a proposal."
        return LearningUpdateProposal(gap=gap, statement=statement, applied=False, limitations=["The learning update was not applied. Weights, source, permissions, and policies were not changed."])

    def apply(self, proposal: LearningUpdateProposal) -> LearningUpdateProposal:
        raise PermissionError("ARC-17 does not apply learning updates")


class EvolutionProposalService:
    def propose(self, learning: LearningUpdateProposal, *, source: str | None) -> EvolutionRecord:
        code = learning.gap if learning.gap in {"simulation_backend_unavailable", "prediction_uncertainty", "planning_failure", "evidence_gap", "tool_gap"} else "tool_gap" if learning.gap == "capability_gap" else "evidence_gap"
        proposal = EvolutionCycle().propose(CapabilityGap(code=code, statement=learning.statement, source=source), approved=False, source=source)
        return EvolutionRecord(gap=code, lifecycle=proposal.lifecycle.value, change=proposal.change.kind, applied=proposal.applied, human_approval=proposal.human_approval, limitations=list(proposal.limitations))
