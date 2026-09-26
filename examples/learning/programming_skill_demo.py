"""Demo A: programming skill. MOCK / DETERMINISTIC. PROPOSAL ONLY. NO REAL-WORLD AUTONOMOUS ADAPTATION."""

from superagi.learning import LearningPipeline, LearningRequest, LearningTask, PracticeEngine, Skill, SkillGraph, SkillPrerequisite, SkillStatus, SkillType, ValidationCriteria

BANNER = ["MOCK / DETERMINISTIC", "PROPOSAL ONLY", "NO REAL-WORLD AUTONOMOUS ADAPTATION"]


def fizzbuzz(n):
    return "FizzBuzz" if n % 15 == 0 else "Fizz" if n % 3 == 0 else "Buzz" if n % 5 == 0 else str(n)


def build():
    graph = SkillGraph()
    graph.add_skill(Skill(name="Python", skill_type=SkillType.PROGRAMMING, status=SkillStatus.DECLARED))
    graph.add_skill(Skill(name="Control Flow", skill_type=SkillType.PROGRAMMING, status=SkillStatus.PROPOSED))
    graph.add_prerequisite(SkillPrerequisite(skill="Control Flow", required="Python"))
    cases = [((3,), "Fizz"), ((5,), "Buzz"), ((15,), "FizzBuzz"), ((7,), "7")]
    engine = PracticeEngine()
    attempts = [engine.code("Control Flow", fizzbuzz, cases, source="demo-tests") for _ in range(2)]
    request = LearningRequest(task=LearningTask(goal="Write FizzBuzz in Python", required_skills=["Control Flow"]), attempts=attempts, criteria=ValidationCriteria(min_passing_episodes=2, require_test_suite=True), test_suite_passed=True, source="demo")
    result = LearningPipeline().run(request, graph=graph)
    return {
        "banner": BANNER,
        "gaps": [f"{gap.gap_type.value}:{gap.subject}" for gap in result.gaps],
        "scores": [attempt.score for attempt in attempts],
        "assessment": [item.status.value for item in result.assessments],
        "validated": [item.validated for item in result.validations],
        "lifecycle": result.lifecycle.value,
        "update_applied": [update.applied for update in result.updates],
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
