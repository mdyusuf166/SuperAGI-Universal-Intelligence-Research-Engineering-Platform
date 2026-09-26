"""Demo B: scientific research skill. MOCK / DETERMINISTIC. PROPOSAL ONLY. NO REAL-WORLD AUTONOMOUS ADAPTATION."""

from superagi.learning import KnowledgeGapDetector, LearningPlanner, PracticeEngine, Skill, SkillAssessment, SkillStatus, SkillType

BANNER = ["MOCK / DETERMINISTIC", "PROPOSAL ONLY", "NO REAL-WORLD AUTONOMOUS ADAPTATION"]


def build():
    gaps = KnowledgeGapDetector().detect(research_evidence=["replication study", "dose-response data"], source="demo-review")
    plan = LearningPlanner().plan("Evaluate a literature claim", gaps, source="demo")
    engine = PracticeEngine()
    attempts = [
        engine.research("Evidence Review", "Claim cites one replication", ["replication study"], ["replication study", "dose-response data"], source="demo"),
        engine.research("Evidence Review", "Claim cites both sources", ["replication study", "dose-response data"], ["replication study", "dose-response data"], source="demo"),
    ]
    skill = Skill(name="Evidence Review", skill_type=SkillType.RESEARCH, status=SkillStatus.PROPOSED)
    assessment = SkillAssessment().assess(skill, attempts, source="demo")
    return {
        "banner": BANNER,
        "gaps": [f"{gap.gap_type.value}:{gap.subject}" for gap in gaps],
        "plan_status": plan.status,
        "plan_steps": [step.skill for step in plan.steps],
        "coverage": [attempt.score for attempt in attempts],
        "assessment": assessment.status.value,
        "metrics": {metric.name: metric.value for metric in assessment.metrics},
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
