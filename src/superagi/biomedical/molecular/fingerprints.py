from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, ConfigDict


class FingerprintResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    molecule_id: UUID | None = None
    fingerprint_type: str = "morgan_r2_128"
    representation: str | None = None
    source: str = "RDKitAdapter"
    status: str
    limitations: list[str] = []


class FingerprintEngine:
    def __init__(self, adapter) -> None: self.adapter = adapter
    def generate(self, smiles: str, molecule_id: UUID | None = None) -> FingerprintResult:
        result = self.adapter.fingerprint(smiles)
        if not result.available:
            return FingerprintResult(molecule_id=molecule_id, status="UNAVAILABLE", limitations=[result.get("error", "RDKit unavailable")])
        if result.get("error"):
            return FingerprintResult(molecule_id=molecule_id, status="FAILED", limitations=[result["error"]])
        return FingerprintResult(molecule_id=molecule_id, representation="".join(result.get("bits", [])), status="COMPUTATIONAL_RESULT")
