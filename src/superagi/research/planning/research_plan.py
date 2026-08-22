from enum import Enum
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ResearchStage(str, Enum):
    LITERATURE_REVIEW = "literature_review"
    EVIDENCE_COLLECTION = "evidence_collection"
    EVIDENCE_EVALUATION = "evidence_evaluation"
    KNOWLEDGE_SYNTHESIS = "knowledge_synthesis"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    HYPOTHESIS_CRITIQUE = "hypothesis_critique"
    EXPERIMENT_DESIGN = "experiment_design"
    VERIFICATION = "verification"
    REPORT_GENERATION = "report_generation"


class ResearchPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID = Field(default_factory=uuid4)
    research_question_id: UUID
    objective: str
    subquestions: tuple[str, ...] = ()
    stages: tuple[ResearchStage, ...] = tuple(ResearchStage)
    dependencies: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    success_criteria: tuple[str, ...] = ()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)
