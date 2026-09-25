from superagi.core.models import AgentResult

from ..control import SIMULATION_CONTROL, SimulationController
from .engineering_agent import EngineeringAgent


class ControlAgent(EngineeringAgent):
    def __init__(self):
        super().__init__("control_agent", ("engineering", "control_design"))

    async def run(self, task, context):
        config = context.values.get("controller")
        if config is None:
            return await super().run(task, context)
        controller = SimulationController()
        if context.values.get("actuator_request"):
            gate = controller.assess_actuator(context.values["actuator_request"])
            return AgentResult(success=gate["allowed"], confidence=0.2, summary="Actuator request stayed inside the ARC-07 simulation boundary.", output={"agent": self.metadata.name, **gate}, limitations=["No actuator command was sent."])
        result = controller.step(config, context.values.get("setpoint", 0.0), context.values.get("measured", 0.0), integral=context.values.get("integral", 0.0), previous_error=context.values.get("previous_error", 0.0))
        return AgentResult(
            success=result.valid and result.classification == SIMULATION_CONTROL and not result.command_sent,
            confidence=0.3,
            summary="Simulation control step; no actuator command.",
            output={"agent": self.metadata.name, "classification": result.classification, "control": result.model_dump()},
            limitations=["SIMULATION_CONTROL only."],
        )
