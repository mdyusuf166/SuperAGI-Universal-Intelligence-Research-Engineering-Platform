from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BiomedicalModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Molecule(BiomedicalModel):
    id: UUID = Field(default_factory=uuid4)
    smiles: str = Field(min_length=1)
    inchi: str | None = None
    name: str | None = None
    formula: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance: tuple[str, ...] = ()


class DNASequence(BiomedicalModel):
    id: UUID = Field(default_factory=uuid4)
    sequence: str = Field(min_length=1)
    length: int = Field(default=0, ge=1)
    alphabet: str = "ACGT"
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance: tuple[str, ...] = ()

    @field_validator("sequence")
    @classmethod
    def normalize_sequence(cls, value: str) -> str:
        return value.upper()

    def model_post_init(self, __context: Any) -> None:
        self.length = len(self.sequence)


class BiomedicalEntityType(str, Enum):
    GENE = "gene"
    PROTEIN = "protein"
    DNA = "dna"
    RNA = "rna"
    MOLECULE = "molecule"
    DRUG = "drug"
    DISEASE = "disease"
    CELL = "cell"
    PATHWAY = "pathway"
    ORGANISM = "organism"
    UNKNOWN = "unknown"


class BiomedicalEntity(BiomedicalModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1)
    entity_type: BiomedicalEntityType = BiomedicalEntityType.UNKNOWN
    description: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance: tuple[str, ...] = ()


class MolecularProperty(BiomedicalModel):
    name: str
    value: float | str | None
    unit: str = ""
    confidence: float = Field(default=0.0, ge=0, le=1)
    source: str
    provenance: tuple[str, ...] = ()


class Prediction(BiomedicalModel):
    id: UUID = Field(default_factory=uuid4)
    prediction_type: str
    model: str
    input: dict[str, Any]
    output: dict[str, Any]
    uncertainty: float | None = Field(default=None, ge=0)
    status: str = "PREDICTED"
    limitations: list[str] = Field(default_factory=list)
    provenance: tuple[str, ...] = ()


class BiomedicalEvidence(BiomedicalModel):
    id: UUID = Field(default_factory=uuid4)
    claim: str
    source: str
    evidence_id: str
    confidence: float = Field(default=0.0, ge=0, le=1)
    limitations: list[str] = Field(default_factory=list)
    provenance: tuple[str, ...] = ()


class BiomedicalResearchResult(BiomedicalModel):
    question: str
    findings: list[dict[str, Any]] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    knowledge_gaps: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    provenance: tuple[str, ...] = ()
