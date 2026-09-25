"""Action proposals stay unexecuted."""

from __future__ import annotations

from .models import ActionProposal, ActionStatus, ProvenanceNote


class ActionProposalService:
    def create(self, *, action: str, reason: str, evidence: list[str], risk: str, constraints: list[str], approval_required: bool, approved: bool, source: str | None) -> ActionProposal:
        status = ActionStatus.APPROVED if approved and approval_required else ActionStatus.PROPOSAL
        cleaned = source.strip() if isinstance(source, str) else ""
        return ActionProposal(action=action, reason=reason, evidence=list(evidence), risk=risk, constraints=list(constraints), approval_required=approval_required, approval_status=status, executed=False, provenance=ProvenanceNote(source=cleaned or None, status="PRESENT" if cleaned else "MISSING"))

    def execute(self, proposal: ActionProposal) -> ActionProposal:
        raise PermissionError("ARC-17 does not execute action proposals")
