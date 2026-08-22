from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
class MotifMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    motif: str; positions: list[int] = Field(default_factory=list); count: int = 0; limitations: list[str] = ["Exact motif matching does not imply biological significance."]
def find_motif(sequence: str, motif: str) -> MotifMatch:
    motif = motif.upper(); positions = [] if not motif else [index for index in range(len(sequence)) if sequence.startswith(motif, index)]
    return MotifMatch(motif=motif, positions=positions, count=len(positions))
