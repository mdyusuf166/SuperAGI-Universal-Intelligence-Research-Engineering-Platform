from __future__ import annotations
from superagi.core.models import AgentContext, AgentResult, Task
from superagi.memory import UniversalMemory
from superagi.research.agents._base import ResearchAgent, metadata
from ..molecular import MolecularEngine
class MolecularAgent(ResearchAgent):
    def __init__(self, engine=None, memory: UniversalMemory | None = None): super().__init__(metadata("molecular", "Molecular computation agent", ("validation", "descriptors", "fingerprints", "similarity"))); self.engine = engine or MolecularEngine(); self.memory = memory
    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        smiles = context.values.get("smiles", task.description); validation = self.engine.validate(smiles); output = {"classification": "COMPUTATIONAL_RESULT", "validation": validation.model_dump(), "descriptors": self.engine.descriptors(smiles).model_dump() if validation.valid else None, "fingerprint": self.engine.fingerprint(smiles).model_dump() if validation.valid else None}
        if context.values.get("compare_smiles") and validation.valid: output["similarity"] = self.engine.similarity(smiles, context.values["compare_smiles"]).model_dump()
        if self.memory: self.memory.remember(str(output), source="molecular_agent", metadata={"classification": "COMPUTATIONAL_RESULT"})
        return AgentResult(success=validation.valid, output=output, summary="Molecular analysis completed.", limitations=["Computational result, not evidence or clinical validation."])
