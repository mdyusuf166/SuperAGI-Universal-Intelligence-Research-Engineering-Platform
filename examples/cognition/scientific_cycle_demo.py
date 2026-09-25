"""Demo A: science hypothesis cycle. SIMULATION ONLY. MOCK / DETERMINISTIC. PROPOSAL ONLY. NO REAL-WORLD EXECUTION."""

from superagi.cognition import CognitivePipeline, CycleRequest, EpistemicStatus, NumericSignal, Observation, ObservationSource
from superagi.memory import UniversalMemory


def build():
    memory = UniversalMemory()
    memory.remember("Moisture note supplied by the user.", source="user-supplied note")
    request = CycleRequest(goal="Draft a science hypothesis about moisture.", question="How might a declared moisture reading relate to growth?", observations=[Observation(statement="The note lists moisture as 3.", source_kind=ObservationSource.USER_INPUT, epistemic=EpistemicStatus.EVIDENCED, evidence_refs=["user-supplied note"])], source="user-supplied note", series=[1, 2, 3], simulate=True, predict=True, signals=[NumericSignal(name="moisture", value=3)], deltas=[NumericSignal(name="moisture", value=1)], assumptions=["The note was supplied by the user."], approval_required=False)
    state = CognitivePipeline().run(request, memory=memory)
    return {"banner": ["SIMULATION ONLY", "MOCK / DETERMINISTIC", "PROPOSAL ONLY", "NO REAL-WORLD EXECUTION"], "lifecycle": state.lifecycle.value, "hypothesis": any(item.epistemic == EpistemicStatus.HYPOTHESIZED for item in state.reasoning_result.inferences), "prediction": state.prediction_result.epistemic.value, "simulation": state.simulation_result.epistemic.value, "plan": state.plan_result.status, "executed": state.executed, "accuracy": state.prediction_result.measured_accuracy}


def main():
    report = build()
    for line in report["banner"]:
        print(line)
    for key, value in report.items():
        print(f"{key}: {value}")
    return report


if __name__ == "__main__":
    main()
