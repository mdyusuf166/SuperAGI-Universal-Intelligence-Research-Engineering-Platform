"""Lessons from experiences. Lessons stay proposals without evidence."""

from __future__ import annotations

from .models import ExperienceKind, ExperienceRecord, Lesson, LessonKind


class ExperienceAnalyzer:
    def analyze(self, experiences: list[ExperienceRecord]) -> list[Lesson]:
        lessons: list[Lesson] = []
        for experience in experiences:
            refs = [str(item.id) for item in experience.evidence]
            status = "EVIDENCED" if refs and experience.kind == ExperienceKind.OBSERVED else "PROPOSED"
            limits = ["One episode is not a general rule."]
            if experience.kind != ExperienceKind.OBSERVED:
                limits.append(f"{experience.kind.value} experience is not real-world experience.")
            if experience.outcome.success is True:
                lessons.append(Lesson(kind=LessonKind.SUCCESSFUL_PATTERN, statement=f"{experience.task} succeeded once.", status=status, experience_kind=experience.kind, evidence_refs=refs, generalized=False, limitations=limits))
            if experience.outcome.success is False:
                lessons.append(Lesson(kind=LessonKind.FAILED_PATTERN, statement=f"{experience.task} failed once.", status=status, experience_kind=experience.kind, evidence_refs=refs, generalized=False, limitations=limits))
            for violation in experience.constraint_violations:
                lessons.append(Lesson(kind=LessonKind.CONSTRAINT_VIOLATION, statement=violation, status=status, experience_kind=experience.kind, evidence_refs=refs, limitations=limits))
            if experience.prediction_error is not None:
                lessons.append(Lesson(kind=LessonKind.PREDICTION_ERROR, statement=f"Supplied prediction error {experience.prediction_error}.", status=status, experience_kind=experience.kind, evidence_refs=refs, limitations=limits))
            if experience.plan and experience.outcome.success is False:
                lessons.append(Lesson(kind=LessonKind.PLANNING_WEAKNESS, statement=f"Plan {experience.plan} did not reach the outcome.", status="PROPOSED", experience_kind=experience.kind, evidence_refs=refs, limitations=limits))
            for name in experience.missing_knowledge:
                lessons.append(Lesson(kind=LessonKind.MISSING_KNOWLEDGE, statement=name, status=status, experience_kind=experience.kind, evidence_refs=refs, limitations=limits))
            for name in experience.missing_skills:
                lessons.append(Lesson(kind=LessonKind.MISSING_SKILL, statement=name, status=status, experience_kind=experience.kind, evidence_refs=refs, limitations=limits))
            if experience.uncertainty:
                lessons.append(Lesson(kind=LessonKind.UNCERTAINTY, statement=experience.uncertainty, status="PROPOSED", experience_kind=experience.kind, evidence_refs=refs, limitations=limits))
        return lessons
