from __future__ import annotations
from pydantic import BaseModel, ConfigDict
class PredictionUncertainty(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: float | None = None; method: str | None = None; interpretation: str = "Backend did not provide uncertainty."; available: bool = False
