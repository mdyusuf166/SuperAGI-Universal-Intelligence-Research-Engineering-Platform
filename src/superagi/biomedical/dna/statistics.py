from __future__ import annotations
from pydantic import BaseModel, ConfigDict

class GCContentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    length: int; gc_content: float | None; status: str = "COMPUTATIONAL_STATISTIC"; limitations: list[str] = ["Sequence statistics do not establish biological or clinical significance."]
class BaseFrequencyResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    length: int; frequencies: dict[str, int]; status: str = "COMPUTATIONAL_STATISTIC"; limitations: list[str] = ["Sequence statistics do not establish biological or clinical significance."]

def gc_content(sequence: str) -> GCContentResult: return GCContentResult(length=len(sequence), gc_content=(sequence.count("G") + sequence.count("C")) / len(sequence) if sequence else None)
def base_frequency(sequence: str) -> BaseFrequencyResult: return BaseFrequencyResult(length=len(sequence), frequencies={base: sequence.count(base) for base in "ATGC"})
