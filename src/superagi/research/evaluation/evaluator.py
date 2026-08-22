from ..hypotheses.models import Hypothesis
from ..reports.models import ResearchReport
from pydantic import BaseModel, ConfigDict, Field
from superagi.memory.evidence import Evidence, EvidenceStatus
from .metrics import calculate_metrics


class EvidenceAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    evidence_id: object
    score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    status: EvidenceStatus
    reasons: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class EvidenceEvaluator:
    def evaluate(self, evidence: Evidence) -> EvidenceAssessment:
        clarity = bool(evidence.claim.strip() and evidence.excerpt.strip())
        source_quality = 0.8 if evidence.source and evidence.source_id else 0.5
        support = evidence.confidence if evidence.status is EvidenceStatus.SUPPORTED else evidence.confidence * 0.5
        score = round((source_quality + (1.0 if clarity else 0.0) + support) / 3, 3)
        return EvidenceAssessment(evidence_id=evidence.id, score=score, confidence=evidence.confidence, status=evidence.status, reasons=["Source metadata present" if source_quality >= 0.8 else "Source identifier is incomplete", "Claim and excerpt are present" if clarity else "Claim or excerpt is unclear"], limitations=["Deterministic assessment; source authority was not independently verified."])


class ResearchEvaluator:
    def evaluate(self, report: ResearchReport, *, evidence_count: int, hypotheses: list[Hypothesis], provenance_count: int) -> dict[str, float]:
        cited = sum(bool(item.get("evidence_ids") or item.get("evidence_id")) for item in report.key_findings)
        return calculate_metrics(evidence_count=evidence_count, cited_finding_count=cited, provenance_count=provenance_count, expected_provenance_count=max(evidence_count, 1), testable_hypothesis_count=sum(bool(item.predictions) for item in hypotheses), hypothesis_count=len(hypotheses), contradiction_count=len(report.verification.get("contradictions", [])), claim_count=max(len(report.key_findings), 1), reproducibility_score=0.5 if report.experiment_proposals else 0.0)
