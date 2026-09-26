"""Demo D: robotics navigation skill. SIMULATION ONLY. MOCK / DETERMINISTIC. PROPOSAL ONLY. NO REAL-WORLD AUTONOMOUS ADAPTATION. No physical robot."""

from superagi.learning import PracticeEngine, Skill, SkillAssessment, SkillStatus, SkillType

BANNER = ["SIMULATION ONLY", "MOCK / DETERMINISTIC", "PROPOSAL ONLY", "NO REAL-WORLD AUTONOMOUS ADAPTATION"]


def build():
    engine = PracticeEngine()
    clear = engine.robot_navigation("Grid Navigation", (0, 0), (3, 0), bounds=(5, 5), source="demo")
    detour = engine.robot_navigation("Grid Navigation", (0, 0), (2, 0), obstacles=((1, 0),), bounds=(5, 5), source="demo")
    blocked = engine.robot_navigation("Grid Navigation", (0, 0), (2, 0), obstacles=((1, 0), (0, 1)), bounds=(3, 3), source="demo")
    skill = Skill(name="Grid Navigation", skill_type=SkillType.ROBOTICS, status=SkillStatus.PROPOSED)
    assessment = SkillAssessment().assess(skill, [clear, detour, blocked], source="demo")
    return {
        "banner": BANNER,
        "modes": [clear.mode.value, detour.mode.value, blocked.mode.value],
        "passed": [clear.passed, detour.passed, blocked.passed],
        "errors": blocked.errors,
        "evidence_kinds": [e.kind.value for e in clear.evidence + detour.evidence],
        "assessment": assessment.status.value,
        "limitations": clear.limitations,
        "physical_robot": False,
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
