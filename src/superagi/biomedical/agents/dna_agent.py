from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from superagi.core.models import AgentContext, AgentResult, Task
from superagi.research.agents._base import ResearchAgent, metadata
from ..dna import DNASequenceAnalyzer
class DNAAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    classification: str = "COMPUTATIONAL_RESULT"; validation: dict; length: int | None = None; gc_content: dict | None = None; base_frequency: dict | None = None; motif: dict | None = None; limitations: list[str] = ["Raw DNA statistics do not support medical conclusions."]
class DNAAgent(ResearchAgent):
    def __init__(self, analyzer=None): super().__init__(metadata("dna", "DNA sequence computation agent", ("validation", "statistics", "motifs", "comparison"))); self.analyzer = analyzer or DNASequenceAnalyzer()
    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        sequence = context.values.get("sequence", task.description); valid = self.analyzer.validate(sequence); result = DNAAnalysisResult(validation=valid.model_dump())
        if valid.valid:
            result.length = self.analyzer.length(sequence); result.gc_content = self.analyzer.gc_content(sequence).model_dump(); result.base_frequency = self.analyzer.base_frequency(sequence).model_dump()
            if context.values.get("motif"): result.motif = self.analyzer.find_motif(sequence, context.values["motif"]).model_dump()
        return AgentResult(success=valid.valid, output=result.model_dump(), summary="DNA analysis completed.", limitations=result.limitations)
