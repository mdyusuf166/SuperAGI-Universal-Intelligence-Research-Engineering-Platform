from .models import Hypothesis, HypothesisStatus


class HypothesisEvaluator:
    def evaluate(self, hypothesis: Hypothesis, evidence_ids=()) -> Hypothesis:
        ids = tuple(evidence_ids) or hypothesis.evidence_ids
        status = HypothesisStatus.SUPPORTED if ids else HypothesisStatus.UNKNOWN
        confidence = min(0.9, 0.5 + 0.1 * len(ids)) if ids else 0.2
        return hypothesis.model_copy(update={"evidence_ids": ids, "status": status, "confidence": confidence})
