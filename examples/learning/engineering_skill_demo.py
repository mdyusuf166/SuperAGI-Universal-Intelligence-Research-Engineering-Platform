"""Demo C: engineering skill. SIMULATION ONLY. MOCK / DETERMINISTIC. PROPOSAL ONLY. NO REAL-WORLD AUTONOMOUS ADAPTATION."""

from superagi.learning import ExperienceKind, ExperienceRecord, KnowledgeGapDetector, LearningOutcome, PracticeEngine, Skill, SkillStatus, SkillType, SkillValidator, ValidationCriteria

BANNER = ["SIMULATION ONLY", "MOCK / DETERMINISTIC", "PROPOSAL ONLY", "NO REAL-WORLD AUTONOMOUS ADAPTATION"]


def build():
    failed = ExperienceRecord(task="Tank level control", kind=ExperienceKind.SIMULATED, evaluation="Level exceeded the limit.", outcome=LearningOutcome(success=False, statement="Constraint violated", kind=ExperienceKind.SIMULATED), constraint_violations=["level > 10"], missing_skills=["Level Control"])
    gaps = KnowledgeGapDetector().detect(experiences=[failed], source="demo-eval")
    engine = PracticeEngine()
    attempts = [engine.simulate("Level Control", {"level": 4.0}, [{"level": 2.0}, {"level": 2.0}], target={"level": 8.0}, bounds={"level": (0.0, 10.0)}, source="demo") for _ in range(2)]
    skill = Skill(name="Level Control", skill_type=SkillType.ENGINEERING, status=SkillStatus.PROPOSED)
    constrained = SkillValidator().validate(skill, attempts, ValidationCriteria(require_constraint_satisfaction=True), constraints_satisfied=all(item.passed for item in attempts))
    observed = SkillValidator().validate(skill, attempts, ValidationCriteria(require_observed=True))
    return {
        "banner": BANNER,
        "gaps": [f"{gap.gap_type.value}:{gap.subject}" for gap in gaps],
        "practice_mode": attempts[0].mode.value,
        "passed": [item.passed for item in attempts],
        "validated_in_simulation": constrained.validated,
        "validation_limits": constrained.limitations,
        "validated_for_real_world": observed.validated,
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
