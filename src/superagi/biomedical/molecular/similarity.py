from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SimilarityResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    molecule_a: str
    molecule_b: str
    score: float | None = None
    method: str = "Morgan fingerprint Tanimoto"
    status: str
    limitations: list[str] = Field(default_factory=list)


class MolecularSimilarity:
    def __init__(self, adapter) -> None: self.adapter = adapter
    def compare(self, molecule_a: str, molecule_b: str) -> SimilarityResult:
        if not self.adapter.available:
            return SimilarityResult(molecule_a=molecule_a, molecule_b=molecule_b, status="UNAVAILABLE", limitations=["RDKit is unavailable; similarity was not calculated."])
        a, b = self.adapter.fingerprint(molecule_a), self.adapter.fingerprint(molecule_b)
        if a.get("error") or b.get("error"):
            return SimilarityResult(molecule_a=molecule_a, molecule_b=molecule_b, status="FAILED", limitations=[a.get("error") or b.get("error")])
        av, bv = a["bits"], b["bits"]
        intersection = sum(x == y == "1" for x, y in zip(av, bv)); union = sum(x == "1" or y == "1" for x, y in zip(av, bv))
        return SimilarityResult(molecule_a=molecule_a, molecule_b=molecule_b, score=intersection / union if union else 1.0, status="COMPUTATIONAL_RESULT")
