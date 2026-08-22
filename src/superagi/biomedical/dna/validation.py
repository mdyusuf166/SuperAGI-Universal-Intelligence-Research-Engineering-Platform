from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field

class DNAValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    valid: bool; input: str | None; normalized_value: str | None = None
    errors: list[str] = Field(default_factory=list); warnings: list[str] = Field(default_factory=list)

def validate_sequence(sequence: str | None) -> DNAValidationResult:
    if not isinstance(sequence, str) or not sequence.strip(): return DNAValidationResult(valid=False, input=sequence, errors=["DNA sequence must be a non-empty string"])
    normalized = sequence.strip().upper(); invalid = sorted(set(normalized) - set("ACGT"))
    return DNAValidationResult(valid=not invalid, input=sequence, normalized_value=normalized, errors=[f"Invalid DNA characters: {''.join(invalid)}"] if invalid else [])
