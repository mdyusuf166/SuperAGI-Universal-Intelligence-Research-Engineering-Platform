"""Demo B: deterministic grid walk. SIMULATION ONLY. MOCK / DETERMINISTIC. NO REAL-WORLD EXECUTION."""

from superagi.evolution import DomainSimulationRegistry, MockSimulationBackend, SimulationAction, SimulationScenario, SimulationState, StateVariable
from superagi.robotics.planning.path_planner import AStarPlanner


def build():
    path = AStarPlanner().plan((0, 0), (2, 0))
    state = SimulationState(variables=[StateVariable(name="x", value=path[0].x), StateVariable(name="y", value=path[0].y)])
    actions = []
    for previous, current in zip(path, path[1:]):
        actions.append(SimulationAction(name=f"step-{int(current.x)}-{int(current.y)}", deltas=[StateVariable(name="x", value=current.x - previous.x), StateVariable(name="y", value=current.y - previous.y)]))
    scenario = SimulationScenario(name="grid-walk", domain="robotics", initial_state=state, actions=actions)
    mock = MockSimulationBackend().run(scenario)
    unavailable = DomainSimulationRegistry().adapter("robotics").simulate(scenario)
    return {
        "banner": ["SIMULATION ONLY", "MOCK / DETERMINISTIC", "NO REAL-WORLD EXECUTION"],
        "path": [{"x": point.x, "y": point.y} for point in path],
        "trace": [{"x": step.value("x"), "y": step.value("y")} for step in mock.trace],
        "mock_classification": mock.classification.value,
        "robotics_backend": unavailable.status.value,
        "executed": False,
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
