from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class HypothesisStatus(str, Enum):
    PROPOSED = "proposed"
    SUPPORTED = "supported"
    WEAK = "weak"
    CONTRADICTED = "contradicted"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


class Hypothesis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID = Field(default_factory=uuid4)
    statement: str = Field(min_length=1)
    rationale: str = ""
    predictions: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    evidence_ids: tuple[UUID, ...] = ()
    confidence: float = Field(default=0.5, ge=0, le=1)
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    metadata: dict[str, Any] = Field(default_factory=dict)
