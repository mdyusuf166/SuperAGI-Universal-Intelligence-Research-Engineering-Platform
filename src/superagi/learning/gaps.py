"""Knowledge-gap detection from explicit requirements and evidence."""

from __future__ import annotations

from .models import ExperienceRecord, GapType, KnowledgeGap, LearningTask, SkillStatus
from .provenance import provenance
from .skills import SkillGraph


def _gap(gap_type: GapType, subject: str, reason: str, evidence: list[str], source: str | None) -> KnowledgeGap:
    return KnowledgeGap(gap_type=gap_type, subject=subject, reason=reason, evidence=list(evidence), confidence=None, confidence_basis="Derived from an explicit requirement or supplied record. Not a probability.", provenance=provenance(source, agent="knowledge_gap_detector", evidence=evidence), limitations=["A gap is a proposal from supplied inputs."])


class KnowledgeGapDetector:
    def detect(self, *, task: LearningTask | None = None, graph: SkillGraph | None = None, known: list[str] | None = None, experiences: list[ExperienceRecord] | None = None, prediction_uncertain: bool = False, planning_failed: bool = False, simulation_unavailable: bool = False, research_evidence: list[str] | None = None, tool_gaps: list[str] | None = None, source: str | None = None) -> list[KnowledgeGap]:
        gaps: list[KnowledgeGap] = []
        have = {item.casefold() for item in known or []}
        if graph is not None:
            have |= {skill.name.casefold() for skill in graph.skills() if skill.status in {SkillStatus.VALIDATED, SkillStatus.DECLARED}}
        if task is not None:
            for name in task.required_knowledge:
                if name.casefold() not in have:
                    gaps.append(_gap(GapType.MISSING_KNOWLEDGE, name, "Required by the task and not declared as known.", [f"task requirement: {name}"], source))
            for name in task.required_skills:
                if name.casefold() not in have:
                    gaps.append(_gap(GapType.MISSING_SKILL, name, "Required by the task and not declared or validated.", [f"task requirement: {name}"], source))
                if graph is not None:
                    try:
                        for need in graph.dependencies(name):
                            if need.casefold() not in have:
                                gaps.append(_gap(GapType.MISSING_SKILL, need, f"Prerequisite of {name} is not declared or validated.", [f"skill graph: {name} requires {need}"], source))
                    except KeyError:
                        gaps.append(_gap(GapType.MISSING_DOMAIN_CAPABILITY, name, "The skill is not present in the skill graph.", [f"task requirement: {name}"], source))
        for experience in experiences or []:
            ref = str(experience.id)
            if experience.outcome.success is False:
                gaps.append(_gap(GapType.FAILED_VALIDATION, experience.task, "A supplied experience failed.", [ref], source))
            if not experience.evidence:
                gaps.append(_gap(GapType.MISSING_EVIDENCE, experience.task, "The experience has no evidence attached.", [ref], source))
            for name in experience.missing_skills:
                gaps.append(_gap(GapType.MISSING_SKILL, name, "Recorded as missing in an experience.", [ref], source))
            for name in experience.missing_knowledge:
                gaps.append(_gap(GapType.MISSING_KNOWLEDGE, name, "Recorded as missing in an experience.", [ref], source))
        if prediction_uncertain:
            gaps.append(_gap(GapType.HIGH_UNCERTAINTY, "prediction", "The caller reported an unevaluated or unknown forecast.", ["prediction uncertainty flag"], source))
        if planning_failed:
            gaps.append(_gap(GapType.INSUFFICIENT_PRACTICE, "planning", "The caller reported a planning failure.", ["planning failure flag"], source))
        if simulation_unavailable:
            gaps.append(_gap(GapType.MISSING_DOMAIN_CAPABILITY, "simulation backend", "A requested simulation backend is unavailable.", ["simulation unavailable flag"], source))
        for item in research_evidence or []:
            gaps.append(_gap(GapType.MISSING_EVIDENCE, item, "Research evidence was requested and not supplied.", [f"research requirement: {item}"], source))
        for item in tool_gaps or []:
            gaps.append(_gap(GapType.MISSING_TOOL, item, "A required tool is not available.", [f"tool requirement: {item}"], source))
        unique: dict[tuple[str, str], KnowledgeGap] = {}
        for gap in gaps:
            unique.setdefault((gap.gap_type.value, gap.subject.casefold()), gap)
        return [unique[key] for key in sorted(unique)]
