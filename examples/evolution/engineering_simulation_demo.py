"""Demo A: declared engineering variables. SIMULATION ONLY. MOCK / DETERMINISTIC. NO REAL-WORLD EXECUTION."""

from superagi.evolution import (
    DomainSimulationRegistry,
    EvolutionPipeline,
    PlanningAction,
    SimulationAction,
    SimulationScenario,
    SimulationState,
    StateVariable,
)


def build():
    state = SimulationState(variables=[StateVariable(name="power", value=5), StateVariable(name="margin", value=1)])
    actions = [SimulationAction(name="reduce-load", deltas=[StateVariable(name="power", value=-1), StateVariable(name="margin", value=0.5)])]
    unavailable = DomainSimulationRegistry().adapter("engineering").simulate(SimulationScenario(name="engineering-fidelity", initial_state=state, actions=actions))
    result = EvolutionPipeline().run(goal="Estimate a declared power margin.", initial_state=state, actions=actions, series=[5, 4], candidates={"primary": [PlanningAction(name="reduce-load", postconditions=["margin reviewed"], deltas=[StateVariable(name="power", value=-1)], cost=1, risk=1, estimated_outcome="Declared margin increases in the mock.")]}, weights={"cost": 1, "risk": 1}, outcome_variable="power", source="declared engineering scenario")
    return {"banner": ["SIMULATION ONLY", "MOCK / DETERMINISTIC", "NO REAL-WORLD EXECUTION"], "domain_status": unavailable.status.value, "domain_classification": unavailable.classification.value, "mock_status": result["status"], "power": [step.value("power") for step in result["simulation"].trace], "prediction": [point.value for point in result["prediction"].points], "executed": result["executed"], "selected": result["comparison"].selected_name}


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
