"""Demo B: engineering proposal cycle. SIMULATION ONLY. MOCK / DETERMINISTIC. PROPOSAL ONLY. NO REAL-WORLD EXECUTION."""

from superagi.cognition import CognitivePipeline, CycleRequest, EpistemicStatus, NumericSignal, Observation, ObservationSource


def build():
    request = CycleRequest(
        goal="Review an engineering design margin.",
        observations=[Observation(statement="Declared power is 5.", source_kind=ObservationSource.USER_INPUT, epistemic=EpistemicStatus.OBSERVED, evidence_refs=["schematic"])],
        source="declared schematic",
        series=[5, 4],
        simulate=True,
        predict=True,
        signals=[NumericSignal(name="power", value=5)],
        deltas=[NumericSignal(name="power", value=-1)],
        constraints=["Declared power stays at or below 6."],
        assumptions=["The schematic was supplied by the user."],
        approval_required=False,
    )
    state = CognitivePipeline().run(request)
    return {"banner": ["SIMULATION ONLY", "MOCK / DETERMINISTIC", "PROPOSAL ONLY", "NO REAL-WORLD EXECUTION"], "lifecycle": state.lifecycle.value, "domain": state.domain_result.selected_winner, "simulation": state.simulation_result.classification, "prediction": state.prediction_result.epistemic.value, "plan_executed": state.plan_result.executed, "executed": state.executed}


def main():
    report = build()
    for line in report["banner"]:
        print(line)
    for key, value in report.items():
        print(f"{key}: {value}")
    return report


if __name__ == "__main__":
    main()
