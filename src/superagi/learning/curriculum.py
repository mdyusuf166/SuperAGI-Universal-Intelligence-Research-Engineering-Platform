"""Learning plans and the ARC-11 education adapter."""

from __future__ import annotations

from superagi.education.models import Curriculum, StudentProfile
from superagi.education.services import KnowledgeGapAnalyzer, LearningPathPlanner

from .models import GapType, KnowledgeGap, LearningObjective, LearningPlan, LearningStep, Skill, SkillPrerequisite, SkillStatus, SkillType, ValidationCriteria
from .provenance import provenance
from .safety import LearningSafetyPolicy
from .skills import SkillGraph


class LearningPlanner:
    def plan(self, goal: str, gaps: list[KnowledgeGap], *, graph: SkillGraph | None = None, effort: dict[str, str] | None = None, criteria: ValidationCriteria | None = None, source: str | None = None) -> LearningPlan:
        LearningSafetyPolicy().guard(goal)
        subjects: list[str] = []
        for gap in gaps:
            names = [gap.subject]
            if graph is not None:
                try:
                    names = graph.dependencies(gap.subject) + [graph.get_skill(gap.subject).name]
                except KeyError:
                    pass
            for name in names:
                if name.casefold() not in {item.casefold() for item in subjects}:
                    subjects.append(name)
        if graph is not None:
            order = {name.casefold(): index for index, name in enumerate(graph.order())}
            subjects.sort(key=lambda name: (order.get(name.casefold(), len(order)), name))
        gap_subjects = {gap.subject.casefold() for gap in gaps}
        if graph is not None:
            known = {skill.name.casefold() for skill in graph.skills() if skill.status in {SkillStatus.DECLARED, SkillStatus.VALIDATED}}
            subjects = [name for name in subjects if name.casefold() in gap_subjects or name.casefold() not in known]
        steps = []
        for name in subjects:
            prereqs = []
            if graph is not None:
                try:
                    prereqs = graph.dependencies(name)
                except KeyError:
                    prereqs = []
            steps.append(LearningStep(skill=name, prerequisites=prereqs, practice_task=f"Practice {name} with supplied exercises.", assessment_criteria=["task_completion", "error_count", "evidence_coverage"], validation=criteria or ValidationCriteria(), effort=(effort or {}).get(name)))
        limits = ["PROPOSAL ONLY: the plan is not executed.", "Effort is shown only when the caller supplies it."]
        if not gaps:
            limits.append("No evidenced gaps were supplied; the plan is empty.")
        if any(step.skill.casefold() not in gap_subjects for step in steps):
            limits.append("Some steps are prerequisites taken from the skill graph.")
        return LearningPlan(goal=goal, steps=steps, provenance=provenance(source, agent="learning_planner"), limitations=limits)


class EducationLearningAdapter:
    """Wraps ARC-11 curriculum planning; it does not re-implement it."""

    def skill_graph(self, curriculum: Curriculum, student: StudentProfile | None = None, *, source: str | None = None) -> SkillGraph:
        declared = {item.casefold() for item in (student.declared_knowledge if student else [])}
        graph = SkillGraph()
        names = {topic.name for topic in curriculum.topics}
        for topic in curriculum.topics:
            for need in topic.prerequisites:
                names.add(need)
        for name in sorted(names):
            status = SkillStatus.DECLARED if name.casefold() in declared else SkillStatus.PROPOSED
            graph.add_skill(Skill(name=name, skill_type=SkillType.EDUCATION, status=status, domain="education", provenance=provenance(source, agent="education_learning_adapter")))
        for topic in curriculum.topics:
            for need in topic.prerequisites:
                graph.add_prerequisite(SkillPrerequisite(skill=topic.name, required=need))
        return graph

    def objectives(self, student: StudentProfile, curriculum: Curriculum, goal: str, *, source: str | None = None) -> list[LearningObjective]:
        plan = LearningPathPlanner().plan(student, curriculum, goal)
        return [LearningObjective(statement=f"Study {task.topic}", skill=task.topic, provenance=provenance(source, agent="education_learning_adapter")) for task in plan.tasks]

    def gaps(self, student: StudentProfile, curriculum: Curriculum, *, source: str | None = None) -> list[KnowledgeGap]:
        found = KnowledgeGapAnalyzer().analyze(student, curriculum)
        return [KnowledgeGap(gap_type=GapType.MISSING_KNOWLEDGE, subject=gap.topic, reason=gap.reason, evidence=[f"missing prerequisite: {item}" for item in gap.evidence], confidence_basis="ARC-11 declared-prerequisite comparison. Not a probability.", provenance=provenance(source, agent="education_learning_adapter"), limitations=["Based on declared knowledge only."]) for gap in found]
