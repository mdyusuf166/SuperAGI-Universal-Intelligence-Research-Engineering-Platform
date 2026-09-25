"""ARC-01 agents that call the cognitive cycle. They do not duplicate domain agents."""

from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from .actions import ActionProposalService
from .context import CognitiveContextBuilder
from .evaluation import CognitiveEvaluator
from .learning import EvolutionProposalService, LearningProposalService
from .loop import CognitiveCycle
from .models import CycleRequest
from .reasoning import BoundedReasoner
from .stages import CognitiveDecisionAdapter, CognitivePlanningAdapter, CognitivePredictionAdapter, CognitiveSimulationAdapter


def _result(agent, summary: str, output: dict) -> AgentResult:
    output = {"agent": agent, "executed": False, **output}
    return AgentResult(success=True, confidence=0.3, summary=summary, output=output, limitations=["Proposal only. No real-world execution."])


class CognitiveCoordinatorAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="cognitive_coordinator_agent", description="Runs one bounded cognitive cycle", capabilities=("cognition",), risk_level="low"))

    async def run(self, task, context):
        request = context.values.get("request") or CycleRequest(goal=task.description, approval_required=False)
        state = CognitiveCycle(memory=context.values.get("memory"), graph=context.values.get("graph")).run(request)
        return _result(self.metadata.name, "Cognitive cycle finished as a proposal.", {"lifecycle": state.lifecycle.value, "executed": state.executed})


class ContextAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="cognitive_context_agent", description="Builds a bounded cognitive context", capabilities=("cognition", "context"), risk_level="low"))

    async def run(self, task, context):
        built = CognitiveContextBuilder().build(goal=context.values.get("goal", task.description), observations=context.values.get("observations", []), memory=context.values.get("memory"), graph=context.values.get("graph"), source=context.values.get("source"))
        return _result(self.metadata.name, "Bounded context.", {"bound": built.bound, "entities": len(built.entities)})


class ReasoningAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="cognitive_reasoning_agent", description="Records structured claims and inferences", capabilities=("cognition", "reasoning"), risk_level="low"))

    async def run(self, task, context):
        result = BoundedReasoner().reason(goal=context.values["goal"], context=context.values["context"], assumptions=context.values.get("assumptions", []))
        return _result(self.metadata.name, "Structured reasoning.", {"inferences": len(result.inferences), "unknowns": len(result.unknowns)})


class SimulationCoordinatorAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="cognitive_simulation_coordinator_agent", description="Calls the ARC-15 simulation backend", capabilities=("cognition", "simulation"), risk_level="low"))

    async def run(self, task, context):
        result = CognitiveSimulationAdapter(context.values.get("backend")).run(signals=context.values.get("signals", []), deltas=context.values.get("deltas", []))
        return _result(self.metadata.name, "Simulation stage.", {"status": result.status, "epistemic": result.epistemic.value})


class PredictionCoordinatorAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="cognitive_prediction_coordinator_agent", description="Calls the ARC-15 prediction engine", capabilities=("cognition", "prediction"), risk_level="low"))

    async def run(self, task, context):
        result = CognitivePredictionAdapter().project(context.values.get("series", []))
        return _result(self.metadata.name, "Prediction stage.", {"epistemic": result.epistemic.value, "measured_accuracy": result.measured_accuracy})


class PlanningCoordinatorAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="cognitive_planning_coordinator_agent", description="Calls the ARC-15 planner", capabilities=("cognition", "planning"), risk_level="low"))

    async def run(self, task, context):
        result = CognitivePlanningAdapter().propose(goal=context.values.get("goal", task.description), signals=context.values.get("signals", []), constraints=context.values.get("constraints", []))
        return _result(self.metadata.name, "Planning proposal.", {"status": result.status, "executed": result.executed})


class DecisionCoordinatorAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="cognitive_decision_coordinator_agent", description="Calls ARC-14 decision support", capabilities=("cognition", "decision"), risk_level="low"))

    async def run(self, task, context):
        result = CognitiveDecisionAdapter().prepare(question=context.values.get("goal", task.description), options=context.values.get("options", ["review"]), criteria=context.values.get("criteria", ["risk"]), evidence=context.values.get("evidence", []), assumptions=context.values.get("assumptions", ["Proposal only."]), risks=["No execution."], human_approved=False)
        return _result(self.metadata.name, "Decision proposal.", {"approved": result.approved, "executed": result.executed, "criteria": result.criteria})


class EvaluationAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="cognitive_evaluation_agent", description="Structural cognitive evaluation", capabilities=("cognition", "evaluation"), risk_level="low"))

    async def run(self, task, context):
        report = CognitiveEvaluator().evaluate(context.values["state"])
        return _result(self.metadata.name, "Evaluation.", {"goal_alignment": report.items[0].status})


class LearningProposalAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="cognitive_learning_proposal_agent", description="Proposes a learning update without applying it", capabilities=("cognition", "learning"), risk_level="low"))

    async def run(self, task, context):
        proposal = LearningProposalService().propose(context.values["state"])
        return _result(self.metadata.name, "Learning proposal.", {"gap": proposal.gap, "applied": proposal.applied})


class EvolutionProposalAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="cognitive_evolution_proposal_agent", description="Proposes an evolution record without applying it", capabilities=("cognition", "evolution"), risk_level="low"))

    async def run(self, task, context):
        learning = context.values.get("learning") or LearningProposalService().propose(context.values["state"])
        record = EvolutionProposalService().propose(learning, source=context.values.get("source"))
        return _result(self.metadata.name, "Evolution proposal.", {"lifecycle": record.lifecycle, "applied": record.applied})


AGENT_CLASSES = (
    CognitiveCoordinatorAgent,
    ContextAgent,
    ReasoningAgent,
    SimulationCoordinatorAgent,
    PredictionCoordinatorAgent,
    PlanningCoordinatorAgent,
    DecisionCoordinatorAgent,
    EvaluationAgent,
    LearningProposalAgent,
    EvolutionProposalAgent,
)
