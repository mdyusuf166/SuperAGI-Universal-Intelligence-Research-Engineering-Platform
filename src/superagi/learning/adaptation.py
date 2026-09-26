"""Adaptation proposals, skill transfer proposals, and cross-domain reuse."""

from __future__ import annotations

from superagi.orchestration.registry import AgentCapabilityRegistry

from .models import AdaptationProposal, SkillClaim, SkillReuseReport, SkillTransferProposal
from .provenance import provenance
from .safety import LearningSafetyPolicy

ADAPTATION_TARGETS = ("planner_strategy", "retrieval_strategy", "skill_ordering", "practice_strategy", "domain_adapter", "tool_recommendation", "knowledge_source", "simulation_strategy")


class AdaptationService:
    def __init__(self) -> None:
        self.safety = LearningSafetyPolicy()

    def propose(self, target: str, reason: str, evidence: list[str], *, expected_benefit: str, risk: str, source: str | None = None) -> AdaptationProposal:
        if target not in ADAPTATION_TARGETS:
            raise ValueError(f"Unsupported adaptation target: {target}")
        self.safety.guard(f"{reason} {expected_benefit}")
        if not evidence:
            raise ValueError("An adaptation proposal needs evidence")
        return AdaptationProposal(target=target, reason=reason, evidence=list(evidence), expected_benefit=expected_benefit, risk=risk, validation_requirement="Re-run the affected evaluation with supplied criteria before any change.", rollback_requirement="Keep the previous configuration so a reviewer can restore it.", provenance=provenance(source, agent="adaptation_service", evidence=evidence), limitations=["PROPOSAL ONLY: not applied.", "Human approval required.", "An adaptation proposal is not autonomous adaptation."])

    def apply(self, proposal: AdaptationProposal) -> None:
        raise PermissionError("Adaptation proposals are never applied automatically")


class TransferService:
    def propose(self, source_skill: str, target_skill: str, shared_abstraction: str, *, assumptions: list[str] | None = None, differences: list[str] | None = None, risks: list[str] | None = None, source: str | None = None) -> SkillTransferProposal:
        LearningSafetyPolicy().guard(f"{source_skill} {target_skill} {shared_abstraction}")
        return SkillTransferProposal(source_skill=source_skill, target_skill=target_skill, shared_abstraction=shared_abstraction, assumptions=list(assumptions or []), differences=list(differences or ["Differences between domains have not been measured."]), risks=list(risks or ["Transfer may not hold in the target domain."]), validation_requirements=[f"Validate {target_skill} with its own criteria and evidence."], provenance=provenance(source, agent="transfer_service"), limitations=["A transfer proposal is not a transfer.", "No transfer success is claimed without validation."])


class CrossDomainSkillReuse:
    def __init__(self, registry: AgentCapabilityRegistry | None = None) -> None:
        self.registry = registry

    def compare(self, skill: str, claims: list[SkillClaim]) -> SkillReuseReport:
        relevant = [claim for claim in claims if claim.skill.casefold() == skill.casefold()]
        statuses = {claim.status for claim in relevant}
        conflict = None
        if len(statuses) > 1:
            conflict = "Domains disagree: " + ", ".join(f"{claim.domain}={claim.status.value}" for claim in sorted(relevant, key=lambda c: c.domain))
        return SkillReuseReport(skill=skill, claims=relevant, conflict=conflict, selected_winner=None)

    def domains_for(self, capabilities: list[str]) -> list[str]:
        if self.registry is None:
            return []
        return sorted({descriptor.capability.domain for descriptor in self.registry.discover(capabilities)})
