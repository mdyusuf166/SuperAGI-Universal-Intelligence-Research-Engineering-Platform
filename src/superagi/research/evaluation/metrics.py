def _ratio(numerator: int, denominator: int) -> float:
    return min(1.0, numerator / denominator) if denominator else 0.0


def calculate_metrics(*, evidence_count: int, cited_finding_count: int, provenance_count: int, expected_provenance_count: int, testable_hypothesis_count: int, hypothesis_count: int, contradiction_count: int, claim_count: int, reproducibility_score: float = 0.0) -> dict[str, float]:
    return {"EvidenceCoverage": _ratio(evidence_count, max(evidence_count, 1)), "CitationCompleteness": _ratio(cited_finding_count, max(claim_count, 1)), "ProvenanceCompleteness": _ratio(provenance_count, max(expected_provenance_count, 1)), "HypothesisTestability": _ratio(testable_hypothesis_count, max(hypothesis_count, 1)), "ContradictionRate": _ratio(contradiction_count, max(claim_count, 1)), "UnsupportedClaimRate": _ratio(max(claim_count - cited_finding_count, 0), max(claim_count, 1)), "ReproducibilityScore": max(0.0, min(1.0, reproducibility_score))}
