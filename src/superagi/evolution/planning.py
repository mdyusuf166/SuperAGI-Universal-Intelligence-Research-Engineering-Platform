"""Deterministic plans composed with the ARC-01 planner. Plans are proposals."""

from __future__ import annotations

from superagi.core.models import Task
from superagi.core.planning import PlanExecutor, Planner
from superagi.core.tasks import TaskManager

from .models import (
    PlanComparison,
    PlanEvaluation,
    PlanRecord,
    PlanStepRecord,
    PlanTerm,
    PlanningAction,
    PlanningProblem,
    PredictionHorizon,
    PredictionMethod,
    PredictionRequest,
    SimulationAction,
    SimulationScenario,
    TerminationCondition,
)
from .prediction import PredictionEngine
from .simulation import MockSimulationBackend


class PlanningEngine:
    def __init__(self) -> None:
        self.tasks = TaskManager()
        self.planner = Planner()

    def plan(self, problem: PlanningProblem) -> PlanRecord:
        core = self.tasks.create_task(problem.goal.statement)
        core_plan = self.planner.create_plan(core)
        facts = set(problem.initial_facts)
        remaining = {action.name: action for action in problem.actions}
        ordered: list[PlanningAction] = []
        while remaining:
            ready = [action for action in remaining.values() if set(action.dependencies) <= {item.name for item in ordered} and set(action.preconditions) <= facts]
            if not ready:
                return PlanRecord(steps=[PlanStepRecord(step_id=action.name, description=action.name, dependencies=list(action.dependencies), action=action.name) for action in ordered], core_plan_steps=[step.description for step in core_plan.steps], status="FAILED", feasible=False, failure="No action satisfies the current preconditions and dependencies.")
            ready.sort(key=lambda action: action.name)
            chosen = ready[0]
            ordered.append(chosen)
            remaining.pop(chosen.name)
            facts.update(chosen.postconditions)
            if problem.goal.statement in facts:
                break
        violations = self._violations(problem, ordered)
        return PlanRecord(steps=[PlanStepRecord(step_id=action.name, description=action.estimated_outcome or action.name, dependencies=list(action.dependencies), action=action.name) for action in ordered], core_plan_steps=[step.description for step in core_plan.steps], status="PROPOSAL", feasible=not violations, failure="; ".join(violations) or None)

    async def execute_core(self, statement: str) -> list[str]:
        task = self.tasks.create_task(statement)
        plan = self.planner.create_plan(task)

        async def handler(step):
            return {"draft": True, "step": step.step_id}

        await PlanExecutor().execute(plan, handler)
        return [step.description for step in plan.steps]

    def _violations(self, problem: PlanningProblem, actions: list[PlanningAction]) -> list[str]:
        total_cost = sum(action.cost for action in actions)
        violations = []
        for constraint in problem.constraints:
            if constraint.kind == "max_cost" and total_cost > constraint.limit:
                violations.append(f"max_cost {total_cost} exceeds {constraint.limit}")
        return violations


class ModelBasedPlanner:
    def __init__(self, backend: MockSimulationBackend | None = None) -> None:
        self.backend = backend or MockSimulationBackend()
        self.engine = PlanningEngine()
        self.predictor = PredictionEngine()

    def compare(self, problem: PlanningProblem, candidates: dict[str, list[PlanningAction]], weights: dict[str, float], outcome_variable: str) -> PlanComparison:
        evaluations = []
        for name, actions in candidates.items():
            scoped = problem.model_copy(deep=True)
            scoped.actions = actions
            plan = self.engine.plan(scoped)
            simulated = None
            predicted = None
            if problem.initial_state is not None:
                scenario = SimulationScenario(name=name, initial_state=problem.initial_state, actions=[SimulationAction(name=action.name, deltas=list(action.deltas)) for action in actions], termination=TerminationCondition(max_steps=max(len(actions), 1)))
                simulated = self.backend.run(scenario)
                if simulated.trace:
                    series = [state.value(outcome_variable) for state in simulated.trace if _has(state, outcome_variable)]
                    if series:
                        predicted = self.predictor.predict(PredictionRequest(series=series, horizon=PredictionHorizon(steps=1), method=PredictionMethod.PERSISTENCE)).points
            outcome = predicted[0].value if predicted else None
            measured = {
                "cost": sum(action.cost for action in actions),
                "risk": sum(action.risk for action in actions),
                "time": float(len(actions)),
                "constraint_violations": float(len(plan.failure.split("; ")) if plan.failure else 0),
                "predicted_outcome": outcome if outcome is not None else 0.0,
                "utility": -sum(action.utility for action in actions),
            }
            terms = [PlanTerm(name=key, weight=weight, measured=measured[key], weighted=weight * measured[key]) for key, weight in sorted(weights.items()) if key in measured]
            evaluations.append(PlanEvaluation(plan_name=name, feasible=plan.feasible, terms=terms, score=sum(term.weighted for term in terms), basis="sum of caller-supplied weight times measured term", constraint_violations=[plan.failure] if plan.failure else [], predicted_outcome=outcome, limitations=["Lowest score is not a verified best plan. Criteria not supplied by the caller are excluded."]))
        evaluations.sort(key=lambda item: (item.score, item.plan_name))
        selected = evaluations[0].plan_name if evaluations else None
        return PlanComparison(evaluations=evaluations, selected_name=selected, basis="Lowest explicit weighted sum, then plan name. Not a hidden overall ranking.", hidden_criteria=False, approved=False, executed=False)


def _has(state, name: str) -> bool:
    try:
        state.value(name)
    except KeyError:
        return False
    return True
