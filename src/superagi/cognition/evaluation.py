"""Structural evaluation. Missing ground truth stays NOT_EVALUABLE."""

from __future__ import annotations

from .models import CognitiveState, EvalItem, EvaluationReport, OutcomeStatus


class CognitiveEvaluator:
    def evaluate(self, state: CognitiveState) -> EvaluationReport:
        items = [
            EvalItem(name="goal_alignment", status="NOT_EVALUABLE", detail="No ground truth was supplied for the goal."),
            EvalItem(name="constraint_satisfaction", status="COMPUTED" if state.plan_result else "NOT_EVALUABLE", detail="Plan feasible." if state.plan_result and state.plan_result.feasible else "No feasibility claim." if state.plan_result is None else "Plan recorded an infeasible proposal."),
            EvalItem(name="evidence_coverage", status="NOT_EVALUABLE" if not state.evidence_refs else "COMPUTED", detail=f"Supplied evidence refs: {len(state.evidence_refs)}. This count is not accuracy."),
            EvalItem(name="provenance_completeness", status="COMPUTED", detail=self._provenance(state)),
            EvalItem(name="prediction_availability", status=self._prediction(state), detail=state.prediction_result.epistemic.value if state.prediction_result else "Prediction was not requested."),
            EvalItem(name="simulation_availability", status=self._simulation(state), detail=state.simulation_result.status if state.simulation_result else "Simulation was not requested."),
            EvalItem(name="plan_validity", status="PROPOSAL" if state.plan_result else "NOT_EVALUABLE", detail="executed is false." if state.plan_result else "No plan."),
            EvalItem(name="safety_status", status="ALLOWED" if state.safety_status and state.safety_status.allowed else "REJECTED" if state.safety_status else "NOT_EVALUABLE", detail="Existing policies were consulted."),
            EvalItem(name="decision_completeness", status="PRESENT" if state.decision_result else "MISSING", detail=state.decision_result.tradeoffs if state.decision_result else "No decision view."),
            EvalItem(name="unknowns", status="COMPUTED", detail=f"Unknown count: {len(state.reasoning_result.unknowns) if state.reasoning_result else 0}."),
            EvalItem(name="contradictions", status="COMPUTED", detail=f"Contradiction count: {len(state.reasoning_result.contradictions) if state.reasoning_result else 0}."),
            EvalItem(name="outcome_status", status=state.feedback.status.value if state.feedback else OutcomeStatus.NOT_EXECUTED.value, detail="Caller-supplied or NOT_EXECUTED. Not a measured real-world outcome."),
        ]
        return EvaluationReport(items=items, limitations=["NOT_EVALUABLE means no ground truth was available. No accuracy was invented."])

    def _provenance(self, state: CognitiveState) -> str:
        missing = [name for name, note in state.provenance.model_dump().items() if isinstance(note, dict) and note.get("status") == "MISSING"]
        return "Missing provenance: " + (", ".join(missing) if missing else "none")

    def _prediction(self, state: CognitiveState) -> str:
        if state.prediction_result is None:
            return "NOT_REQUESTED"
        if state.prediction_result.epistemic.value == "UNKNOWN":
            return "NOT_EVALUABLE"
        return "PREDICTED"

    def _simulation(self, state: CognitiveState) -> str:
        if state.simulation_result is None:
            return "NOT_REQUESTED"
        return state.simulation_result.status
