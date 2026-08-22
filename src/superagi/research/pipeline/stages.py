from typing import Any

from pydantic import BaseModel, ConfigDict


class ResearchStageOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    stage: str
    artifact: Any
    provenance_ids: list[str] = []
