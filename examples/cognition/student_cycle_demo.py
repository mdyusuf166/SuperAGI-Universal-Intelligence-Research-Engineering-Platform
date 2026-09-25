"""Demo D: student study plan. SIMULATION ONLY. MOCK / DETERMINISTIC. PROPOSAL ONLY. NO REAL-WORLD EXECUTION."""

from superagi.cognition import CognitivePipeline, CycleRequest, EpistemicStatus, Observation, ObservationSource
from superagi.education.services import AcademicIntegrityPolicy


def build():
    request = CycleRequest(
        goal="Build a student study plan for fractions.",
        observations=[Observation(statement="The learner asked for practice on fractions.", source_kind=ObservationSource.USER_INPUT, epistemic=EpistemicStatus.EVIDENCED, evidence_refs=["learner request"])],
        source="learner request",
        assumptions=["Practice and explanation only."],
        approval_required=False,
    )
    state = CognitivePipeline().run(request)
    return {"banner": ["SIMULATION ONLY", "MOCK / DETERMINISTIC", "PROPOSAL ONLY", "NO REAL-WORLD EXECUTION"], "lifecycle": state.lifecycle.value, "domain": state.domain_result.selected_winner, "integrity": AcademicIntegrityPolicy().assess(request.goal)["allowed"], "learning_gap": state.learning_update.gap, "learning_applied": state.learning_update.applied, "plan_executed": state.plan_result.executed, "executed": state.executed}


def main():
    report = build()
    for line in report["banner"]:
        print(line)
    for key, value in report.items():
        print(f"{key}: {value}")
    return report


if __name__ == "__main__":
    main()
