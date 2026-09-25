"""Demo C: robot grid simulation. SIMULATION ONLY. MOCK / DETERMINISTIC. PROPOSAL ONLY. NO REAL-WORLD EXECUTION."""

from superagi.cognition import CognitivePipeline, CycleRequest, EpistemicStatus, NumericSignal, Observation, ObservationSource
from superagi.world_model import WorldModelDomainRegistry


def build():
    request = CycleRequest(
        goal="Simulate a robot grid step.",
        observations=[Observation(statement="Declared start cell is x=0.", source_kind=ObservationSource.USER_INPUT, epistemic=EpistemicStatus.OBSERVED, evidence_refs=["declared start cell"])],
        source="declared start cell",
        series=[0, 1],
        simulate=True,
        predict=True,
        signals=[NumericSignal(name="x", value=0), NumericSignal(name="y", value=0)],
        deltas=[NumericSignal(name="x", value=1)],
        assumptions=["The start cell was declared by the user."],
        approval_required=False,
    )
    state = CognitivePipeline().run(request)
    backend = WorldModelDomainRegistry().adapter("robotics").import_backend()
    return {"banner": ["SIMULATION ONLY", "MOCK / DETERMINISTIC", "PROPOSAL ONLY", "NO REAL-WORLD EXECUTION"], "lifecycle": state.lifecycle.value, "domain": state.domain_result.selected_winner, "simulation": state.simulation_result.epistemic.value, "predicted": state.prediction_result.epistemic.value, "robotics_backend": backend.status, "safety": state.safety_status.allowed, "executed": state.executed}


def main():
    report = build()
    for line in report["banner"]:
        print(line)
    for key, value in report.items():
        print(f"{key}: {value}")
    return report


if __name__ == "__main__":
    main()
