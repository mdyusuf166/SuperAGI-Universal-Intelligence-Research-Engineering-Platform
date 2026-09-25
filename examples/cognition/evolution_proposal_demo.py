"""Demo E: evolution proposal. SIMULATION ONLY. MOCK / DETERMINISTIC. PROPOSAL ONLY. NO REAL-WORLD EXECUTION."""

from superagi.cognition import CognitivePipeline, CycleRequest, LearningProposalService, NumericSignal
from superagi.evolution.simulation import UnavailableSimulationBackend


def build():
    request = CycleRequest(goal="Record the missing simulator as a capability gap.", simulate=True, signals=[NumericSignal(name="gap", value=1)], approval_required=True, human_approved=False, source="registry")
    state = CognitivePipeline().run(request, simulation_backend=UnavailableSimulationBackend())
    refused = False
    try:
        LearningProposalService().apply(state.learning_update)
    except PermissionError:
        refused = True
    return {
        "banner": ["SIMULATION ONLY", "MOCK / DETERMINISTIC", "PROPOSAL ONLY", "NO REAL-WORLD EXECUTION"],
        "lifecycle": state.lifecycle.value,
        "simulation": state.simulation_result.status,
        "learning_gap": state.learning_update.gap,
        "evolution": state.evolution_proposal.lifecycle,
        "evolution_applied": state.evolution_proposal.applied,
        "apply_refused": refused,
        "executed": state.executed,
    }


def main():
    report = build()
    for line in report["banner"]:
        print(line)
    for key, value in report.items():
        print(f"{key}: {value}")
    return report


if __name__ == "__main__":
    main()
