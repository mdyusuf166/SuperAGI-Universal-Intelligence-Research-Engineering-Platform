from superagi.core.models import AgentResult

from ..circuits import CircuitSimulator, CircuitValidator
from .engineering_agent import EngineeringAgent


class CircuitDesignAgent(EngineeringAgent):
    def __init__(self):
        super().__init__("circuit_design_agent", ("engineering", "circuit_design"))

    async def run(self, task, context):
        circuit = context.values.get("circuit")
        if circuit is None:
            return await super().run(task, context)
        validation = CircuitValidator().validate(circuit)
        simulation = CircuitSimulator(available=bool(context.values.get("simulation_available", False))).simulate(circuit)
        return AgentResult(
            success=validation["valid"],
            confidence=0.3,
            summary="Conceptual circuit validation; no physical execution.",
            output={"agent": self.metadata.name, "classification": "CONCEPTUAL CIRCUIT", "validation": validation, "simulation": simulation},
            limitations=["Conceptual netlist only; not electrical validation."],
        )
