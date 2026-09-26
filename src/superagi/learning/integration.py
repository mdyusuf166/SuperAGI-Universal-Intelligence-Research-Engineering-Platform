"""Memory, personal, world-model, and cognitive adapters for learning records."""

from __future__ import annotations

from superagi.cognition.models import CognitiveState
from superagi.collaboration.models import Consent, Preference
from superagi.collaboration.safety import ConsentGate, SafetyPolicy
from superagi.memory.evidence.evidence import Evidence
from superagi.memory.models import MemoryType
from superagi.memory.service import UniversalMemory
from superagi.world_model.graph import KnowledgeGraph
from superagi.world_model.models import EntityProperty, EntityStatus, EntityType, EpistemicStatus, PropertyValue, RelationType, WorldEntity, WorldRelation
from superagi.world_model.provenance import provenance_from

from .models import ExperienceKind, ExperienceRecord, GapType, KnowledgeGap, LearningObjective, LearningOutcome, LearningProposal, SkillStatus
from .provenance import provenance
from .safety import LearningSafetyPolicy
from .skills import SkillGraph


class LearningMemoryAdapter:
    def __init__(self, memory: UniversalMemory) -> None:
        self.memory = memory

    def store_experience(self, record: ExperienceRecord, *, personal: bool = False, consent: Consent | None = None):
        text = f"[{record.kind.value}] {record.task}: {record.lesson or record.evaluation or record.outcome.statement or 'no lesson'}"
        LearningSafetyPolicy().guard(text)
        if personal and not ConsentGate().persistent_allowed(consent):
            raise PermissionError("Persistent consent is required for personal learning context")
        source = record.provenance.source or "learning"
        stored = self.memory.remember(text, memory_type=MemoryType.EPISODIC, source=source, source_id=str(record.id), tags=("learning", record.kind.value.lower()), metadata={"experience_kind": record.kind.value, "provenance_status": record.provenance.status, "truth": "NOT_ASSERTED"})
        evidence = None
        if record.evidence and record.provenance.source:
            first = record.evidence[0]
            evidence = self.memory.add_evidence(Evidence(claim=first.statement, source=record.provenance.source, source_type=record.kind.value.lower(), source_id=str(first.id), excerpt=record.task))
        return stored, evidence


class PersonalLearningAdapter:
    def objectives(self, *, goals: list = (), projects: list = (), learning: list = (), preferences: list[Preference] = (), source: str | None = None) -> list[LearningObjective]:
        policy = SafetyPolicy()
        for preference in preferences:
            policy.check_preference(preference)
        found = []
        for goal in goals:
            found.append(LearningObjective(statement=f"Goal: {goal.title}", provenance=provenance(source, agent="personal_learning_adapter")))
        for project in projects:
            found.append(LearningObjective(statement=f"Project: {project.name}", provenance=provenance(source, agent="personal_learning_adapter")))
        for item in learning:
            found.append(LearningObjective(statement=f"Learn {item.topic} (declared progress {item.progress})", skill=item.topic, provenance=provenance(source, agent="personal_learning_adapter")))
        for objective in found:
            LearningSafetyPolicy().guard(objective.statement)
        return found


_EPISTEMIC = {SkillStatus.VALIDATED: EpistemicStatus.EVIDENCED, SkillStatus.DECLARED: EpistemicStatus.UNKNOWN, SkillStatus.PROPOSED: EpistemicStatus.HYPOTHESIZED, SkillStatus.PRACTICED: EpistemicStatus.UNKNOWN, SkillStatus.EVALUATED: EpistemicStatus.UNKNOWN, SkillStatus.UNKNOWN: EpistemicStatus.UNKNOWN}


class WorldModelLearningAdapter:
    def link_skills(self, graph: KnowledgeGraph, skills: SkillGraph, *, source: str | None = None) -> list[WorldEntity]:
        created = {}
        for skill in skills.skills():
            entity = WorldEntity(entity_type=EntityType.CONCEPT, name=f"skill:{skill.name}", status=EntityStatus.PROPOSED, epistemic=_EPISTEMIC[skill.status], provenance=provenance_from(source, agent="world_model_learning_adapter"))
            created[skill.name] = graph.add_entity(entity)
        for skill in skills.skills():
            for need in skills.prerequisites(skill.name):
                graph.add_relation(WorldRelation(source_id=created[skill.name].id, relation=RelationType.REQUIRES, target_id=created[need].id, epistemic=EpistemicStatus.HYPOTHESIZED, basis="Declared skill prerequisite. Not observed mastery.", provenance=provenance_from(source, agent="world_model_learning_adapter")))
        return list(created.values())

    def annotate(self, graph: KnowledgeGraph, entity: WorldEntity, name: str, value: str, kind: ExperienceKind, *, source: str | None = None):
        epistemic = {ExperienceKind.SIMULATED: EpistemicStatus.SIMULATED, ExperienceKind.PREDICTED: EpistemicStatus.PREDICTED}.get(kind, EpistemicStatus.HYPOTHESIZED)
        return graph.add_annotation(entity.id, EntityProperty(name=name, value=PropertyValue(text=value), epistemic=epistemic, provenance=provenance_from(source, agent="world_model_learning_adapter")))


_GAP_CODES = {
    "simulation_backend_unavailable": GapType.MISSING_DOMAIN_CAPABILITY,
    "prediction_uncertainty": GapType.HIGH_UNCERTAINTY,
    "evidence_gap": GapType.MISSING_EVIDENCE,
    "knowledge_gap": GapType.MISSING_KNOWLEDGE,
    "capability_gap": GapType.MISSING_DOMAIN_CAPABILITY,
}


class CognitiveLearningAdapter:
    """Consumes an ARC-17 CognitiveState. It does not change ARC-17."""

    def experiences(self, state: CognitiveState, *, source: str | None = None) -> list[ExperienceRecord]:
        records = []
        for observation in state.observations:
            kind = ExperienceKind.OBSERVED if observation.epistemic.value in {"OBSERVED", "EVIDENCED"} else ExperienceKind.UNKNOWN
            records.append(ExperienceRecord(task=state.goal, kind=kind, observation=observation.statement, provenance=provenance(source, agent="cognitive_learning_adapter", evidence=observation.evidence_refs)))
        if state.simulation_result is not None:
            records.append(ExperienceRecord(task=state.goal, kind=ExperienceKind.SIMULATED, simulation_result=f"{state.simulation_result.status} {state.simulation_result.classification}", provenance=provenance(source, agent="cognitive_learning_adapter")))
        if state.prediction_result is not None:
            records.append(ExperienceRecord(task=state.goal, kind=ExperienceKind.PREDICTED, prediction=f"{state.prediction_result.method} {state.prediction_result.values}", uncertainty=state.prediction_result.uncertainty, provenance=provenance(source, agent="cognitive_learning_adapter")))
        if state.plan_result is not None:
            outcome = LearningOutcome(success=False if not state.plan_result.feasible else None, statement="Plan proposal was infeasible." if not state.plan_result.feasible else "Plan proposal only; not executed.", kind=ExperienceKind.SYNTHETIC)
            records.append(ExperienceRecord(task=state.goal, kind=ExperienceKind.SYNTHETIC, plan=state.plan_result.status, outcome=outcome, provenance=provenance(source, agent="cognitive_learning_adapter")))
        return records

    def gaps(self, state: CognitiveState, *, source: str | None = None) -> list[KnowledgeGap]:
        gaps = []
        if state.learning_update is not None:
            gap_type = _GAP_CODES.get(state.learning_update.gap, GapType.MISSING_DOMAIN_CAPABILITY)
            gaps.append(KnowledgeGap(gap_type=gap_type, subject=state.learning_update.gap, reason=state.learning_update.statement, evidence=[f"ARC-17 learning_update: {state.learning_update.gap}"], confidence_basis="Copied from an ARC-17 proposal. Not a probability.", provenance=provenance(source, agent="cognitive_learning_adapter"), limitations=["The ARC-17 learning update is itself a proposal."]))
        if state.evaluation is not None:
            for item in state.evaluation.items:
                if item.name == "goal_alignment" and item.status == "NOT_EVALUABLE":
                    gaps.append(KnowledgeGap(gap_type=GapType.MISSING_EVIDENCE, subject="goal ground truth", reason=item.detail, evidence=[f"ARC-17 evaluation: {item.name}={item.status}"], provenance=provenance(source, agent="cognitive_learning_adapter")))
        if state.plan_result is not None and not state.plan_result.feasible:
            gaps.append(KnowledgeGap(gap_type=GapType.INSUFFICIENT_PRACTICE, subject="planning", reason="The ARC-17 plan proposal was infeasible.", evidence=["ARC-17 plan_result.feasible=False"], provenance=provenance(source, agent="cognitive_learning_adapter")))
        return gaps

    def proposal(self, state: CognitiveState, *, source: str | None = None) -> LearningProposal:
        gaps = self.gaps(state, source=source)
        return LearningProposal(gaps=gaps, statement=f"Learning proposal for {state.goal}: {len(gaps)} evidenced gaps.", provenance=provenance(source, agent="cognitive_learning_adapter"), limitations=["A learning proposal is not learning execution.", "Not applied."])
