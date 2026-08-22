from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from superagi.core.models import AgentContext, AgentResult, Task
from superagi.research.hypotheses.models import Hypothesis

from ._base import ResearchAgent, metadata


class Critique(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID = Field(default_factory=uuid4)
    hypothesis_id: UUID
    testability: str
    falsifiability: str
    assumptions: list[str] = Field(default_factory=list)
    evidence_support: list[str] = Field(default_factory=list)
    alternative_explanations: list[str] = Field(default_factory=list)
    potential_confounders: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class CriticAgent(ResearchAgent):
    def __init__(self) -> None:
        super().__init__(metadata("critic_agent", "Critiques testability and confounders", ("hypothesis_critique", "confounder_analysis")))

    def critique(self, hypothesis: Hypothesis) -> Critique:
        return Critique(hypothesis_id=hypothesis.id, testability="Testable with repeated measurements", falsifiability="Falsifiable if predicted changes are absent", assumptions=list(hypothesis.assumptions), evidence_support=[str(item) for item in hypothesis.evidence_ids], alternative_explanations=["Unmeasured environmental or system factors"], potential_confounders=["Temperature", "Irradiance", "System degradation"], limitations=["This critique is analytical; it is not validation."])

    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        hypotheses = [Hypothesis.model_validate(item) if isinstance(item, dict) else item for item in context.values.get("hypotheses", [])]
        critiques = [self.critique(item) for item in hypotheses]
        return AgentResult(success=True, confidence=0.6, summary=f"Critiqued {len(critiques)} hypotheses", output={"critiques": [item.model_dump() for item in critiques]})
