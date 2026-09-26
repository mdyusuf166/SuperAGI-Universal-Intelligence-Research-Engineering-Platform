"""Demo E: adaptive proposal. MOCK / DETERMINISTIC. PROPOSAL ONLY. NO REAL-WORLD AUTONOMOUS ADAPTATION."""

from superagi.cognition import CognitivePipeline, CycleRequest
from superagi.evolution import UnavailableSimulationBackend
from superagi.learning import AdaptationService, CognitiveLearningAdapter

BANNER = ["MOCK / DETERMINISTIC", "PROPOSAL ONLY", "NO REAL-WORLD AUTONOMOUS ADAPTATION"]


def build():
    state = CognitivePipeline().run(CycleRequest(goal="Estimate reactor warm-up", simulate=True, source="demo"), simulation_backend=UnavailableSimulationBackend())
    adapter = CognitiveLearningAdapter()
    proposal = adapter.proposal(state, source="demo")
    gap = proposal.gaps[0]
    service = AdaptationService()
    adaptation = service.propose("simulation_strategy", gap.reason, gap.evidence, expected_benefit="A registered backend could produce simulated evidence.", risk="Simulated evidence may still differ from reality.", source="demo")
    try:
        service.apply(adaptation)
        applied_attempt = "applied"
    except PermissionError as exc:
        applied_attempt = f"refused: {exc}"
    return {
        "banner": BANNER,
        "cognitive_gap": state.learning_update.gap if state.learning_update else None,
        "learning_gaps": [f"{item.gap_type.value}:{item.subject}" for item in proposal.gaps],
        "learning_applied": proposal.applied,
        "adaptation_target": adaptation.target,
        "adaptation_status": adaptation.status.value,
        "adaptation_applied": adaptation.applied,
        "apply_attempt": applied_attempt,
        "human_approval_required": True,
        "executed": False,
    }


def main():
    report = build()
    for line in BANNER:
        print(line)
    for key, value in report.items():
        print(f"{key}: {value}")
    return report


if __name__ == "__main__":
    main()
