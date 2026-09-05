"""Typed, proposal-only artifacts for ARC-12 Scientific Intelligence."""
from __future__ import annotations
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field
class ScienceModel(BaseModel): model_config = ConfigDict(extra="forbid", validate_assignment=True)
class ScientificDomain(str, Enum):
    PHYSICS="Physics"; CHEMISTRY="Chemistry"; BIOLOGY="Biology"; GENETICS="Genetics"; MOLECULAR_BIOLOGY="Molecular Biology"; NEUROSCIENCE="Neuroscience"; COMPUTER_SCIENCE="Computer Science"; AI="AI"; ROBOTICS="Robotics"; QUANTUM_COMPUTING="Quantum Computing"; MATERIALS_SCIENCE="Materials Science"; EARTH_SCIENCE="Earth Science"; SPACE_SCIENCE="Space Science"; ENGINEERING="Engineering"; BIOMEDICAL_SCIENCE="Biomedical Science"; INTERDISCIPLINARY="Interdisciplinary Science"
class KnowledgeKind(str, Enum): FACT="FACT"; EVIDENCE="EVIDENCE"; INFERENCE="INFERENCE"; HYPOTHESIS="HYPOTHESIS"; UNKNOWN="UNKNOWN"; CONTRADICTION="CONTRADICTION"
class HypothesisStatus(str, Enum): PROPOSED="PROPOSED"; SUPPORTED="SUPPORTED"; CONTRADICTED="CONTRADICTED"; UNTESTED="UNTESTED"
class RelationshipKind(str, Enum): CORRELATION="correlation"; CAUSAL_HYPOTHESIS="causal hypothesis"; KNOWN_MECHANISM="known mechanism"
class ScientificQuestion(ScienceModel):
    id: UUID = Field(default_factory=uuid4); question: str = Field(min_length=1); domain: list[str] = Field(default_factory=list); subdomains: list[str] = Field(default_factory=list); objectives: list[str] = Field(default_factory=list); assumptions: list[str] = Field(default_factory=list); constraints: list[str] = Field(default_factory=list); variables: list[str] = Field(default_factory=list); known_facts: list[str] = Field(default_factory=list); unknowns: list[str] = Field(default_factory=list); evidence_refs: list[str] = Field(default_factory=list); provenance_refs: list[str] = Field(default_factory=list)
class KnowledgeItem(ScienceModel): statement: str; kind: KnowledgeKind; evidence_refs: list[str] = Field(default_factory=list); provenance_refs: list[str] = Field(default_factory=list); rationale: str = ""
class ScientificVariable(ScienceModel): id: UUID = Field(default_factory=uuid4); name: str; role: str = "independent"; unit: str = ""; description: str = ""; constraints: list[str] = Field(default_factory=list)
class Parameter(ScienceModel): name: str; value: float | str | None = None; unit: str = ""; description: str = ""
class Constraint(ScienceModel): description: str; variable: str | None = None
class Observation(ScienceModel): description: str; variable: str | None = None; value: float | str | None = None; evidence_refs: list[str] = Field(default_factory=list)
class Equation(ScienceModel): id: UUID = Field(default_factory=uuid4); expression: str; variables: list[str] = Field(default_factory=list); parameters: list[Parameter] = Field(default_factory=list); limitations: list[str] = Field(default_factory=list)
class Hypothesis(ScienceModel):
    id: UUID = Field(default_factory=uuid4); hypothesis: str; rationale: str; supporting_evidence: list[str] = Field(default_factory=list); contradictory_evidence: list[str] = Field(default_factory=list); assumptions: list[str] = Field(default_factory=list); predicted_observations: list[str] = Field(default_factory=list); confounders: list[str] = Field(default_factory=list); confidence: float = Field(default=0, ge=0, le=1); status: HypothesisStatus = HypothesisStatus.PROPOSED
class Cause(ScienceModel): name: str
class Effect(ScienceModel): name: str
class Mechanism(ScienceModel): description: str; evidence_refs: list[str] = Field(default_factory=list)
class Relationship(ScienceModel): cause: Cause; effect: Effect; kind: RelationshipKind = RelationshipKind.CAUSAL_HYPOTHESIS; mechanism: Mechanism | None = None; evidence_refs: list[str] = Field(default_factory=list)
class ExperimentProposal(ScienceModel): id: UUID = Field(default_factory=uuid4); objective: str; variables: list[str] = Field(default_factory=list); controls: list[str] = Field(default_factory=list); measurements: list[str] = Field(default_factory=list); expected_observations: list[str] = Field(default_factory=list); falsification_criteria: list[str] = Field(default_factory=list); risks: list[str] = Field(default_factory=list); reproducibility: str = "NON-EXECUTING proposal; no physical execution."
class SimulationResult(ScienceModel): id: UUID = Field(default_factory=uuid4); backend: str; status: str; output: dict[str, Any] = Field(default_factory=dict); limitations: list[str] = Field(default_factory=list)
class CrossDomainResearchPlan(ScienceModel): id: UUID = Field(default_factory=uuid4); domains: list[str]; contributions: dict[str, str] = Field(default_factory=dict); dependencies: list[str] = Field(default_factory=list)
class ScientificReport(ScienceModel): question: ScientificQuestion; summary: str; conclusions: list[KnowledgeItem] = Field(default_factory=list); limitations: list[str] = Field(default_factory=list); provenance_refs: list[str] = Field(default_factory=list)
