"""ARC-15 and ARC-14 stage adapters. These do not create second engines."""

from __future__ import annotations

from superagi.collaboration.decisions import DecisionSupport
from superagi.evolution.models import EvolutionGoal, PlanningAction, PlanningProblem, PredictionHorizon, PredictionMethod, PredictionRequest, StateVariable
from superagi.evolution.planning import ModelBasedPlanner, PlanningEngine
from superagi.evolution.prediction import PredictionEngine
from superagi.evolution.simulation import MockSimulationBackend, UnavailableSimulationBackend
from superagi.world_model.adapters import SimulationAdapter

from .models import CognitivePredictionResult, CognitiveSimulationResult, DecisionView, EpistemicStatus, NumericSignal, PlanProposal


class CognitiveSimulationAdapter:
    def __init__(self, backend=None) -> None:
        self.backend = backend if backend is not None else MockSimulationBackend()

    def run(self, *, signals: list[NumericSignal], deltas: list[NumericSignal]) -> CognitiveSimulationResult:
        if isinstance(self.backend, UnavailableSimulationBackend):
            return CognitiveSimulationResult(status="SIMULATION_BACKEND_UNAVAILABLE", classification="BACKEND_UNAVAILABLE", epistemic=EpistemicStatus.UNKNOWN, limitations=["SIMULATION_BACKEND_UNAVAILABLE. No mock trajectory was substituted by this adapter."])
        if not signals:
            return CognitiveSimulationResult(status="NOT_REQUESTED", classification="SIMULATION_ONLY", epistemic=EpistemicStatus.UNKNOWN, limitations=["No declared signals were supplied."])
        from superagi.world_model.graph import KnowledgeGraph
        from superagi.world_model.models import EntityStatus as WorldEntityStatus
        from superagi.world_model.models import EntityType, EpistemicStatus as WorldEpistemic
        from superagi.world_model.models import WorldEntity
        from superagi.world_model.provenance import provenance_from
        from superagi.world_model.temporal import Timeline

        graph = KnowledgeGraph()
        holder = graph.add_entity(WorldEntity(entity_type=EntityType.SYSTEM, name="cognitive-signals", status=WorldEntityStatus.PROPOSED, epistemic=WorldEpistemic.UNKNOWN, provenance=provenance_from(None)))
        linked = SimulationAdapter(self.backend).run(graph, Timeline(), entity_id=holder.id, variables=[(item.name, item.value) for item in signals], deltas=[(item.name, item.value) for item in deltas] or [(signals[0].name, 0.0)], source=None)
        if not linked.stored:
            status = "SIMULATION_BACKEND_UNAVAILABLE" if linked.classification == "BACKEND_UNAVAILABLE" else linked.classification
            return CognitiveSimulationResult(status=status, classification=linked.classification, epistemic=EpistemicStatus.UNKNOWN, limitations=linked.limitations)
        values = [NumericSignal(name=item.property.name, value=item.property.value.number or 0.0) for item in graph.annotations_for(holder.id)]
        return CognitiveSimulationResult(status="COMPLETED", classification=linked.classification, epistemic=EpistemicStatus.SIMULATED, values=values, limitations=linked.limitations)


class CognitivePredictionAdapter:
    def __init__(self, engine: PredictionEngine | None = None) -> None:
        self.engine = engine or PredictionEngine()

    def project(self, series: list[float], *, horizon: int = 1) -> CognitivePredictionResult:
        if len(series) < 1:
            return CognitivePredictionResult(method=PredictionMethod.PERSISTENCE.value, horizon=horizon, epistemic=EpistemicStatus.UNKNOWN, confidence=None, confidence_basis="No series was supplied.", uncertainty="UNKNOWN", limitations=["No prediction was stored."])
        output = self.engine.predict(PredictionRequest(series=series, horizon=PredictionHorizon(steps=horizon), method=PredictionMethod.LINEAR_TREND if len(series) > 1 else PredictionMethod.PERSISTENCE, assumptions=["Baseline forecast from the caller-supplied series."]))
        if not output.points:
            return CognitivePredictionResult(method=output.method.value, horizon=horizon, epistemic=EpistemicStatus.UNKNOWN, confidence=0.0, confidence_basis=output.confidence.basis, measured_accuracy=output.confidence.measured_accuracy, uncertainty=output.uncertainty.statement, limitations=output.limitations)
        return CognitivePredictionResult(method=output.method.value, horizon=horizon, values=[point.value for point in output.points], epistemic=EpistemicStatus.PREDICTED, confidence=output.confidence.value, confidence_basis=output.confidence.basis, measured_accuracy=output.confidence.measured_accuracy, uncertainty=output.uncertainty.statement, limitations=output.limitations + ["Stored as PREDICTED. Not an observation."])


class CognitivePlanningAdapter:
    def propose(self, *, goal: str, signals: list[NumericSignal], constraints: list[str]) -> PlanProposal:
        from superagi.evolution.models import SimulationState

        action = PlanningAction(name="review-context", cost=1, risk=0, estimated_outcome="Review the bounded context. Do not execute an external action.")
        initial = SimulationState(variables=[StateVariable(name=item.name, value=item.value) for item in signals]) if signals else None
        problem = PlanningProblem(goal=EvolutionGoal(statement=goal), actions=[action], initial_state=initial)
        plan = PlanningEngine().plan(problem)
        basis = "ARC-15 planner proposal. executed is false."
        if signals:
            basis = ModelBasedPlanner().compare(problem, {"primary": [action]}, {"cost": 1.0}, signals[0].name).basis
        return PlanProposal(status="PROPOSAL", steps=[step.step_id for step in plan.steps] or ["review-context"], feasible=plan.feasible, executed=False, basis=basis, limitations=["The plan is a proposal.", "executed is false.", *constraints[:4]])


class CognitiveDecisionAdapter:
    def prepare(self, *, question: str, options: list[str], criteria: list[str], evidence: list[str], assumptions: list[str], risks: list[str], human_approved: bool) -> DecisionView:
        names = options or ["review", "hold"]
        payload = [{"name": name, "criteria": {"risk": 1}, "evidence": evidence, "assumptions": assumptions} for name in names]
        prepared = DecisionSupport().prepare(question=question, options=payload, criteria=criteria or ["risk"], evidence=evidence, assumptions=assumptions, risks=risks, tradeoffs="Lowest explicit criterion sum, then name. Not a hidden policy.")
        decision = prepared["decision"]
        if human_approved:
            DecisionSupport().approve(decision, human=True)
        return DecisionView(question=decision.question, options=list(decision.options), criteria=list(decision.criteria), evidence=list(decision.evidence), assumptions=list(decision.assumptions), risks=list(decision.risks), tradeoffs=decision.tradeoffs, uncertainty="Caller-supplied criteria are not objective correctness.", approved=decision.approved, status=decision.status, human_approval_required=True, executed=False)
