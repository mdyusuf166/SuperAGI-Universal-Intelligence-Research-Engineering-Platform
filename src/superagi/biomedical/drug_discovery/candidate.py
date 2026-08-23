from __future__ import annotations
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field

class DrugCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    candidate_id: UUID = Field(default_factory=uuid4); molecule_id: UUID; molecular_properties: dict[str, float | int] = Field(default_factory=dict); predictions: list[object] = Field(default_factory=list); evidence: list[str] = Field(default_factory=list); status: str = "PROPOSED CANDIDATE"; limitations: list[str] = Field(default_factory=lambda: ["Computational proposal only; not an approved drug or clinical claim."])
