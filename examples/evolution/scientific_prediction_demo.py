"""Demo C: hypothesis, mock simulation, baseline prediction, and a plan proposal."""

from superagi.evolution import (
    EvolutionPipeline,
    PlanningAction,
    PredictionEngine,
    PredictionHorizon,
    PredictionMethod,
    PredictionRequest,
    SimulationAction,
    SimulationState,
    StateVariable,
)
from superagi.science.experiment import ExperimentDesigner
from superagi.science.hypothesis import HypothesisGenerator
from superagi.science.models import ScientificQuestion


def build():
    question = ScientificQuestion(question="How might a declared moisture reading change under a mock intervention?", variables=["moisture"], evidence_refs=["user-supplied series"], assumptions=["The series was supplied by the user."])
    hypothesis = HypothesisGenerator().generate(question)
    experiment = ExperimentDesigner().design(question)
    state = SimulationState(variables=[StateVariable(name="moisture", value=3)])
    actions = [SimulationAction(name="mock-intervention", deltas=[StateVariable(name="moisture", value=1)])]
    prediction = PredictionEngine().predict(PredictionRequest(series=[1, 2, 3], horizon=PredictionHorizon(steps=2), method=PredictionMethod.LINEAR_TREND, evidence=[], assumptions=["The line is fit only to the supplied series."]))
    result = EvolutionPipeline().run(goal="Draft a non-executing observation plan.", initial_state=state, actions=actions, series=[1, 2, 3], candidates={"primary": [PlanningAction(name="record-series", postconditions=["series recorded"], deltas=[StateVariable(name="moisture", value=1)], cost=1, risk=0, estimated_outcome="Record the supplied series.")]}, weights={"cost": 1}, outcome_variable="moisture", source="user-supplied series")
    return {
        "banner": ["SIMULATION ONLY", "MOCK / DETERMINISTIC", "NO REAL-WORLD EXECUTION"],
        "hypothesis": hypothesis.hypothesis,
        "hypothesis_status": hypothesis.status.value,
        "experiment": experiment.reproducibility,
        "prediction": [point.value for point in prediction.points],
        "prediction_accuracy": prediction.confidence.measured_accuracy,
        "moisture": [step.value("moisture") for step in result["simulation"].trace],
        "plan": result["comparison"].selected_name,
        "executed": result["executed"],
    }


def main():
    report = build()
    print("SIMULATION ONLY")
    print("MOCK / DETERMINISTIC")
    print("NO REAL-WORLD EXECUTION")
    for key, value in report.items():
        print(f"{key}: {value}")
    return report


if __name__ == "__main__":
    main()
