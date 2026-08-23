from __future__ import annotations
from superagi.core.models import AgentContext, AgentResult, Task
from superagi.research.agents._base import ResearchAgent, metadata
from ..models import Molecule
from ..chemistry import ChemistryEngine
class ChemistryAgent(ResearchAgent):
    def __init__(self, engine=None): super().__init__(metadata("chemistry", "Chemistry prediction agent", ("properties", "prediction", "uncertainty"))); self.engine = engine or ChemistryEngine()
    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        molecule = context.values.get("molecule") or Molecule(smiles=context.values.get("smiles", task.description)); molecule = Molecule(**molecule) if isinstance(molecule, dict) else molecule
        prediction = self.engine.predict_property(molecule, context.values.get("property", "unspecified"), context.values.get("backend", "deepchem"))
        output = {"classification": "PREDICTION", "properties": self.engine.calculate_properties(molecule).model_dump(), "prediction": prediction.model_dump()}
        return AgentResult(success=prediction.status != "FAILED", output=output, summary="Chemistry analysis completed.", limitations=prediction.limitations)
