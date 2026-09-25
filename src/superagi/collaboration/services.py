"""Review of collaboration artifacts. Critical findings are not accepted."""

from __future__ import annotations

from .models import ReviewFinding, ReviewSeverity
from .safety import SafetyPolicy


class CollaborationReview:
    def __init__(self) -> None:
        self.policy = SafetyPolicy()

    def review(self, session, *, approval_granted: bool = False, orchestration_conflicts: list | None = None) -> dict:
        findings: list[ReviewFinding] = [ReviewFinding(category="decision_boundary", message="The human remains the decision maker.", severity=ReviewSeverity.INFO)]
        if not session.objective or not session.goals:
            findings.append(ReviewFinding(category="missing_requirements", message="Objective or goals are missing.", severity=ReviewSeverity.ERROR))
        for task in session.tasks:
            if not task.owner:
                findings.append(ReviewFinding(category="unclear_ownership", message=f"Task has no owner: {task.title}", severity=ReviewSeverity.ERROR))
            if not task.title or task.title.casefold() in {"tbd", "todo"}:
                findings.append(ReviewFinding(category="ambiguous_tasks", message="A task title is empty or ambiguous.", severity=ReviewSeverity.ERROR))
            if task.blockers:
                findings.append(ReviewFinding(category="unresolved_conflicts", message=f"Blocker remains on {task.title}.", severity=ReviewSeverity.WARNING))
            if not task.evidence and not task.completion_criteria:
                findings.append(ReviewFinding(category="missing_evidence", message=f"Task lacks evidence and completion criteria: {task.title}", severity=ReviewSeverity.WARNING))
        if session.conflicts:
            findings.append(ReviewFinding(category="unresolved_conflicts", message="Conflicting claims are unresolved.", severity=ReviewSeverity.ERROR))
        if any("unsupported" in question.casefold() for question in session.unresolved_questions):
            findings.append(ReviewFinding(category="unsupported_claims", message="An unsupported claim remains in the session.", severity=ReviewSeverity.ERROR))
        if not session.provenance:
            findings.append(ReviewFinding(category="provenance_gaps", message="No provenance reference was supplied.", severity=ReviewSeverity.ERROR))
        safety = self.policy.assess(session.objective)
        if not safety["allowed"]:
            findings.append(ReviewFinding(category="safety_issues", message="Safety policy rejected the objective.", severity=ReviewSeverity.CRITICAL))
        if session.mode.value in {"HUMAN_APPROVAL_REQUIRED", "HUMAN_REVIEW_REQUIRED"} and not approval_granted:
            findings.append(ReviewFinding(category="missing_approval", message="Human approval has not been recorded.", severity=ReviewSeverity.ERROR))
        if orchestration_conflicts:
            findings.append(ReviewFinding(category="unresolved_conflicts", message="Orchestration conflicts remain listed and were not auto-resolved.", severity=ReviewSeverity.WARNING))
        severities = {item.severity for item in findings}
        if ReviewSeverity.CRITICAL in severities:
            status, accepted = "REJECTED", False
        elif ReviewSeverity.ERROR in severities:
            status, accepted = "PARTIALLY_REVIEWED", False
        elif any(item.severity == ReviewSeverity.WARNING for item in findings):
            status, accepted = "PARTIALLY_REVIEWED", True
        else:
            status, accepted = "VERIFIED", True
        return {"findings": findings, "status": status, "accepted": accepted, "issues": [f"{item.severity}: {item.category}: {item.message}" for item in findings]}
