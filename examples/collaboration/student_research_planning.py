"""Demo B: student research planning. Academic integrity stays intact."""

from superagi.collaboration import Consent, ConsentState, InteractionMode, RoleAssigner, CollaborationPipeline
from superagi.education import AcademicIntegrityPolicy, CurriculumManager, KnowledgeGapAnalyzer, LearningPathPlanner, StudentProfile


def build():
    objective = "Plan a study sequence for research methods."
    integrity = AcademicIntegrityPolicy().assess(objective)
    student = StudentProfile(name="student", declared_knowledge=["question scoping"])
    curriculum = CurriculumManager().create("research methods", [
        {"name": "question scoping", "prerequisites": []},
        {"name": "evidence review", "prerequisites": ["question scoping"]},
        {"name": "experiment design", "prerequisites": ["evidence review"]},
    ])
    plan = LearningPathPlanner().plan(student, curriculum, objective)
    gaps = KnowledgeGapAnalyzer().analyze(student, curriculum)
    roles = [RoleAssigner().assign("student", "decision maker", ["Choose the study order"], human=True)]
    result = CollaborationPipeline().run(
        objective,
        participants=["student"],
        roles=roles,
        consent=Consent(state=ConsentState.GRANTED, scope=["session"], persistent=False),
        mode=InteractionMode.HUMAN_REVIEW_REQUIRED,
        goal_statements=["Complete the declared research-methods prerequisites."],
        task_specs=[{"title": task.topic, "owner": "student", "evidence": ["declared curriculum"], "completion_criteria": ["Student reviews the topic"]} for task in plan.tasks],
        milestones=("prerequisites", "research tasks", "review"),
        evidence=("declared curriculum",),
        sources=("declared curriculum",),
        approval=False,
    )
    return {
        "classification": "ASSISTANCE_ONLY",
        "integrity_allowed": integrity["allowed"],
        "status": result["status"],
        "executed": result["executed"],
        "prerequisites": student.declared_knowledge,
        "learning_tasks": [task.topic for task in plan.tasks],
        "gaps": [gap.topic for gap in gaps],
        "milestones": [item.name for goal in result["goals"] for item in goal.milestones],
        "review": result["review"]["status"],
        "approval": result["human_approval"],
        "report": result["report"],
    }


def main():
    report = build()
    print("ASSISTANCE_ONLY")
    print("STUDY PLAN — NOT AN EXAM ANSWER")
    for key in ("integrity_allowed", "status", "prerequisites", "learning_tasks", "gaps", "milestones", "review", "approval", "report"):
        print(f"{key}: {report[key]}")
    return report


if __name__ == "__main__":
    main()
