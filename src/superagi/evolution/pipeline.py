"""Proposal pipeline from a declared state to a human review. Nothing here is executed externally."""

from __future__ import annotations

from superagi.collaboration.decisions import DecisionSupport

from .models import (
    EvolutionGoal,
    PlanningProblem,
    PredictionHorizon,
    PredictionMethod,
    PredictionRequest,
    SimulationScenario,
    TerminationCondition,
    WorldEntity,
)
from .planning import ModelBasedPlanner
from .prediction import PredictionEngine
from .safety import EvolutionSafetyPolicy
from .simulation import MockSimulationBackend
from .world_model import WorldModel


class EvolutionPipeline:
    def run(self, *, goal: str, initial_state, actions, series: list[float], candidates: dict, weights: dict[str, float], outcome_variable: str, source: str | None = None, approval: bool = False) -> dict:
        safety = EvolutionSafetyPolicy().assess(goal)
        if not safety["allowed"]:
            return {"status": "FAILED", "reason": "Safety policy rejected request.", "safety": safety, "executed": False, "classification": "SIMULATION_ONLY"}
        world = WorldModel()
        world.add_entity(WorldEntity(name="scenario", properties=list(initial_state.variables)))
        scenario = SimulationScenario(name=goal, initial_state=initial_state, actions=list(actions), termination=TerminationCondition(max_steps=max(len(actions), 1)))
        simulation = MockSimulationBackend().run(scenario)
        prediction = PredictionEngine().predict(PredictionRequest(series=series, horizon=PredictionHorizon(steps=1), method=PredictionMethod.PERSISTENCE, evidence=[], assumptions=["Persistence uses the last observed value."], provenance=None))
        problem = PlanningProblem(goal=EvolutionGoal(statement=goal), initial_facts=[], actions=list(candidates.get("primary", [])), constraints=[], initial_state=initial_state)
        comparison = ModelBasedPlanner().compare(problem, candidates, weights, outcome_variable)
        decision = DecisionSupport().prepare(question=goal, options=[{"name": comparison.selected_name or "none", "criteria": weights or {"risk": 1}, "evidence": [source or ""], "assumptions": ["The score uses only supplied weights."]}], criteria=list(weights), evidence=[source] if source else [], assumptions=["The human reviews the proposal."], risks=["Mock simulation is not physical fidelity."], tradeoffs=comparison.basis)
        if approval:
            DecisionSupport().approve(decision["decision"], human=True)
        return {
            "status": "COMPLETED" if simulation.status.value == "COMPLETED" else simulation.status.value,
            "classification": "SIMULATION_ONLY",
            "simulation_classification": simulation.classification.value,
            "world_model": world.summary(),
            "simulation": simulation,
            "prediction": prediction,
            "comparison": comparison,
            "decision_status": decision["decision"].status,
            "decision_approved": decision["decision"].approved,
            "executed": False,
            "safety": safety,
            "provenance_missing": source is None,
        }
