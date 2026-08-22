from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class DescriptorResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    molecule_id: UUID | None = None
    descriptors: dict[str, float | int] = Field(default_factory=dict)
    units: dict[str, str] = Field(default_factory=dict)
    source: str = "RDKitAdapter"
    status: str
    limitations: list[str] = Field(default_factory=list)


class DescriptorEngine:
    def __init__(self, adapter) -> None: self.adapter = adapter
    def calculate(self, smiles: str, molecule_id: UUID | None = None) -> DescriptorResult:
        result = self.adapter.descriptors(smiles)
        if not result.available:
            return DescriptorResult(molecule_id=molecule_id, status="UNAVAILABLE", limitations=[result.get("error", "RDKit unavailable")])
        if result.get("error"):
            return DescriptorResult(molecule_id=molecule_id, status="FAILED", limitations=[result["error"]])
        return DescriptorResult(molecule_id=molecule_id, descriptors=result.get("descriptors", {}), units={"molecular_weight": "g/mol"}, status="COMPUTATIONAL_RESULT", limitations=["Computed descriptors are not experimental measurements."])
