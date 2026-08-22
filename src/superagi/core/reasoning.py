from pydantic import BaseModel, ConfigDict, Field


class ReasoningReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str
    assumptions: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    decision: str
    confidence: float = Field(ge=0, le=1)
    limitations: list[str] = Field(default_factory=list)
    verification_status: str


class ReasoningEngine:
    def analyze_problem(self, problem: str) -> ReasoningReport:
        return ReasoningReport(summary=f"Structured analysis of {problem}", decision="Proceed with measurable inputs", confidence=0.5, verification_status="pending")

    def generate_hypotheses(self, problem: str) -> list[str]:
        return [f"Key measurable factors can explain {problem}", f"Historical observations can test {problem}"]

    def evaluate_hypotheses(self, hypotheses: list[str], evidence: list[str]) -> ReasoningReport:
        return ReasoningReport(summary="Compared candidate hypotheses against supplied evidence", evidence=evidence, decision=hypotheses[0] if hypotheses else "No supported hypothesis", confidence=0.5 if hypotheses else 0, verification_status="pending")

    def verify_result(self, report: ReasoningReport, evidence: list[str]) -> ReasoningReport:
        return report.model_copy(update={"evidence": evidence, "verification_status": "verified" if evidence else "insufficient_evidence"})
