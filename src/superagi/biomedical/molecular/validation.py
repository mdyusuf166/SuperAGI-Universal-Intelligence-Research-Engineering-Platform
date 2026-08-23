from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from ..models import AdapterStatus


class MoleculeValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    valid: bool
    input: str | None
    normalized_value: str | None = None
    errors: list[str] = []
    warnings: list[str] = []
    adapter_status: AdapterStatus


class MoleculeValidator:
    def __init__(self, adapter) -> None:
        self.adapter = adapter

    def validate(self, smiles: str | None) -> MoleculeValidationResult:
        if not isinstance(smiles, str) or not smiles.strip():
            return MoleculeValidationResult(valid=False, input=smiles, errors=["SMILES must be a non-empty string"], adapter_status=AdapterStatus.INVALID_INPUT)
        normalized = smiles.strip()
        result = self.adapter.validate_smiles(normalized)
        if not result.available:
            return MoleculeValidationResult(valid=False, input=smiles, normalized_value=normalized, errors=[result.get("error", "RDKit unavailable")], adapter_status=AdapterStatus.UNAVAILABLE)
        if not result.get("valid", False):
            return MoleculeValidationResult(valid=False, input=smiles, normalized_value=normalized, errors=[result.get("error", "Invalid SMILES")], adapter_status=AdapterStatus.INVALID)
        return MoleculeValidationResult(valid=True, input=smiles, normalized_value=normalized, adapter_status=AdapterStatus.AVAILABLE)
