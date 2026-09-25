"""Quality checks. Missing ground truth stays NOT_EVALUABLE."""

from __future__ import annotations

from .models import EvolutionProposal, PredictionOutput, QualityEvaluation, ReviewFinding, ReviewSeverity, SimulationResult
from .safety import EvolutionSafetyPolicy


class MetaEvaluator:
    def simulation(self, result: SimulationResult, reference: list[float] | None = None) -> QualityEvaluation:
        if reference is None:
            return QualityEvaluation(subject="simulation", status="NOT_EVALUABLE", basis="No reference trajectory was supplied.", limitations=["A completed mock run is not a quality score."])
        if not result.trace or len(reference) != len(result.trace):
            return QualityEvaluation(subject="simulation", status="NOT_EVALUABLE", basis="Reference length does not match the trace.", limitations=["No score was invented."])
        return QualityEvaluation(subject="simulation", status="COMPUTED", score=float(len(reference)), basis="Reference length matched the trace. This is not a fidelity score.", limitations=["Matching length is not physical accuracy."])

    def prediction(self, output: PredictionOutput, actual: list[float] | None = None) -> QualityEvaluation:
        if actual is None or len(actual) != len(output.points):
            return QualityEvaluation(subject="prediction", status="NOT_EVALUABLE", basis="No aligned ground truth was supplied.", limitations=["Declared heuristic confidence is not accuracy."])
        error = sum(abs(point.value - truth) for point, truth in zip(output.points, actual)) / len(actual)
        return QualityEvaluation(subject="prediction", status="COMPUTED", score=error, basis="Mean absolute error on the supplied pairs.", limitations=["This error is only for the supplied pairs."])

    def proposal(self, proposal: EvolutionProposal) -> QualityEvaluation:
        missing = []
        if proposal.provenance is None or proposal.provenance.missing:
            missing.append("provenance")
        if not proposal.validation_requirement:
            missing.append("validation")
        if not proposal.rollback_requirement:
            missing.append("rollback")
        if missing:
            return QualityEvaluation(subject="evolution_proposal", status="NOT_EVALUABLE", basis="Required review fields are missing: " + ", ".join(missing), limitations=["Missing fields were not filled in."])
        return QualityEvaluation(subject="evolution_proposal", status="REVIEWED", score=None, basis="Required proposal fields are present. No improvement was measured.", limitations=["Presence of fields is not evidence the change would help."])


class EvolutionReview:
    def review(self, proposal: EvolutionProposal) -> dict:
        findings = [ReviewFinding(category="approval", message="A human must approve any change. ARC-15 does not apply it.", severity=ReviewSeverity.INFO)]
        if proposal.provenance is None or proposal.provenance.missing:
            findings.append(ReviewFinding(category="provenance", message="Provenance source is missing.", severity=ReviewSeverity.ERROR))
        if not proposal.validation_requirement:
            findings.append(ReviewFinding(category="validation", message="Validation requirement is missing.", severity=ReviewSeverity.ERROR))
        if not EvolutionSafetyPolicy().assess(proposal.change.statement)["allowed"]:
            findings.append(ReviewFinding(category="safety", message="The proposed change is not allowed.", severity=ReviewSeverity.CRITICAL))
        if not proposal.human_approval:
            findings.append(ReviewFinding(category="approval", message="Human approval has not been recorded.", severity=ReviewSeverity.WARNING))
        severities = {item.severity for item in findings}
        accepted = ReviewSeverity.ERROR not in severities and ReviewSeverity.CRITICAL not in severities
        status = "REJECTED" if ReviewSeverity.CRITICAL in severities else "PARTIALLY_REVIEWED" if not accepted or ReviewSeverity.WARNING in severities else "REVIEWED"
        return {"findings": findings, "accepted": accepted, "status": status}
