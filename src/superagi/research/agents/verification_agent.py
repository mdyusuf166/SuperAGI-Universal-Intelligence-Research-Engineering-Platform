from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from superagi.core.models import AgentContext, AgentResult, Task
from superagi.research.reports.models import ResearchReport

from ._base import ResearchAgent, metadata


class VerificationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str
    issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    checked_items: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)


class ResearchVerifier:
    def verify(self, *, evidence, hypotheses, report, provenance) -> VerificationReport:
        issues = []
        for finding in report.key_findings:
            if not finding.get("evidence_ids"):
                issues.append("Finding lacks an evidence reference")
        if not evidence:
            issues.append("No evidence was collected")
        status = "verified" if not issues and provenance else "incomplete"
        return VerificationReport(status=status, issues=issues, warnings=["Verification is structural and deterministic; it is not experimental validation."], confidence=0.85 if status == "verified" else 0.25, checked_items=["evidence references", "hypothesis references", "unsupported claims", "provenance completeness"])


class VerificationAgent(ResearchAgent):
    def __init__(self) -> None:
        super().__init__(metadata("verification_agent", "Checks references and structural consistency", ("verification", "integrity_checks")))
        self.verifier = ResearchVerifier()

    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        report = ResearchReport.model_validate(context.values["report"])
        verification = self.verifier.verify(evidence=context.values.get("evidence", []), hypotheses=context.values.get("hypotheses", []), report=report, provenance=context.values.get("provenance", []))
        return AgentResult(success=not verification.issues, confidence=verification.confidence, summary=verification.status, output={"verification": verification.model_dump()})
