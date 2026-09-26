"""Grounded skill assessment and criteria-based validation."""

from __future__ import annotations

from .models import AssessmentMetric, AssessmentStatus, ExperienceKind, LearningAssessment, PracticeAttempt, Skill, SkillStatus, ValidationCriteria, ValidationResult
from .provenance import provenance


class SkillAssessment:
    def assess(self, skill: Skill, attempts: list[PracticeAttempt], *, plan_valid: bool | None = None, observed: bool = False, source: str | None = None) -> LearningAssessment:
        evaluable = [item for item in attempts if item.passed is not None]
        metrics = []
        if evaluable:
            done = sum(1 for item in evaluable if item.passed)
            metrics.append(AssessmentMetric(name="task_completion", status="COMPUTED", value=done / len(evaluable), detail=f"{done}/{len(evaluable)} evaluable attempts passed"))
        else:
            metrics.append(AssessmentMetric(name="task_completion", status="NOT_EVALUABLE", detail="No evaluable attempts"))
        simulated = [item for item in evaluable if item.mode.value == "SIMULATED_PRACTICE"]
        if simulated:
            ok = sum(1 for item in simulated if item.passed)
            metrics.append(AssessmentMetric(name="constraint_satisfaction", status="COMPUTED", value=ok / len(simulated), detail="Simulated constraints only"))
        else:
            metrics.append(AssessmentMetric(name="constraint_satisfaction", status="NOT_EVALUABLE", detail="No simulated constraint checks"))
        metrics.append(AssessmentMetric(name="error_count", status="COMPUTED", value=float(sum(len(item.errors) for item in attempts)), detail="Recorded errors"))
        if attempts:
            covered = sum(1 for item in attempts if item.evidence)
            metrics.append(AssessmentMetric(name="evidence_coverage", status="COMPUTED", value=covered / len(attempts), detail=f"{covered}/{len(attempts)} attempts carry evidence"))
        else:
            metrics.append(AssessmentMetric(name="evidence_coverage", status="NOT_EVALUABLE", detail="No attempts"))
        metrics.append(AssessmentMetric(name="plan_validity", status="NOT_EVALUABLE" if plan_valid is None else "SUPPLIED", value=None if plan_valid is None else float(plan_valid), detail="Caller-supplied plan validity"))
        if evaluable:
            status = AssessmentStatus.EVALUATED
        elif attempts:
            status = AssessmentStatus.PRACTICED
        elif observed:
            status = AssessmentStatus.OBSERVED
        elif skill.status == SkillStatus.DECLARED:
            status = AssessmentStatus.DECLARED
        else:
            status = AssessmentStatus.UNKNOWN
        return LearningAssessment(skill=skill.name, status=status, metrics=metrics, provenance=provenance(source, agent="skill_assessment"), limitations=["Assessment is not validation.", "Metrics cover supplied attempts only."])


class SkillValidator:
    def validate(self, skill: Skill, attempts: list[PracticeAttempt], criteria: ValidationCriteria | None = None, *, ground_truth_match: bool | None = None, test_suite_passed: bool | None = None, constraints_satisfied: bool | None = None, llm_claim: str | None = None) -> ValidationResult:
        criteria = criteria or ValidationCriteria()
        reasons = []
        passing = [item for item in attempts if item.passed is True and item.evidence]
        if len(passing) < criteria.min_passing_episodes:
            reasons.append(f"needs {criteria.min_passing_episodes} evidenced passing episodes, has {len(passing)}")
        if criteria.require_ground_truth and ground_truth_match is not True:
            reasons.append("ground truth match not supplied")
        if criteria.require_test_suite and test_suite_passed is not True:
            reasons.append("test suite pass not supplied")
        if criteria.require_constraint_satisfaction and constraints_satisfied is not True:
            reasons.append("constraint satisfaction not supplied")
        if criteria.require_observed and not any(e.kind == ExperienceKind.OBSERVED for item in passing for e in item.evidence):
            reasons.append("no observed evidence; simulated or synthetic practice does not count")
        validated = not reasons
        limits = ["Validation holds only for the stated criteria.", "Validation is not universal competence."]
        if llm_claim:
            limits.append("The supplied LLM claim was ignored; it is not validation evidence.")
        if validated and all(e.kind != ExperienceKind.OBSERVED for item in passing for e in item.evidence):
            limits.append("Validated on synthetic or simulated evidence only, not real-world competence.")
        return ValidationResult(skill=skill.name, validated=validated, reasons=reasons or ["criteria satisfied"], criteria=criteria, limitations=limits)
