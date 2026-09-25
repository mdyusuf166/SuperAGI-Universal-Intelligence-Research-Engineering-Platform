"""Demo D: a capability-gap proposal. It is not applied."""

from superagi.evolution import CapabilityGap, EvolutionCycle


def build():
    cycle = EvolutionCycle()
    proposal = cycle.propose(CapabilityGap(code="simulation_backend_unavailable", statement="No domain-fidelity simulator is configured.", source="registry"), source="registry")
    refused = False
    try:
        cycle.apply(proposal)
    except PermissionError:
        refused = True
    return {
        "banner": ["SIMULATION ONLY", "MOCK / DETERMINISTIC", "NO REAL-WORLD EXECUTION"],
        "lifecycle": proposal.lifecycle.value,
        "states": [state.value for state in proposal.states_visited],
        "change": proposal.change.kind,
        "applied": proposal.applied,
        "apply_refused": refused,
        "human_approval": proposal.human_approval,
        "version": proposal.version,
    }


def main():
    report = build()
    print("SIMULATION ONLY")
    print("MOCK / DETERMINISTIC")
    print("NO REAL-WORLD EXECUTION")
    print("PROPOSAL ONLY")
    for key, value in report.items():
        print(f"{key}: {value}")
    return report


if __name__ == "__main__":
    main()
