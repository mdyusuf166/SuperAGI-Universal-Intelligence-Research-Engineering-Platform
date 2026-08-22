from __future__ import annotations
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field
from .uncertainty import PredictionUncertainty
class PredictionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prediction_id: UUID = Field(default_factory=uuid4); molecule_id: UUID | None = None; property: str; value: float | str | None = None; unit: str = ""; model: str; backend: str; uncertainty: PredictionUncertainty = Field(default_factory=PredictionUncertainty); status: str; source: str; limitations: list[str] = Field(default_factory=list)
