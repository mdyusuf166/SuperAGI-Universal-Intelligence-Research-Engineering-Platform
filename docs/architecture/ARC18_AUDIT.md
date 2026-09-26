# ARC-18 Audit

## Architecture

ARC-18 adds `src/superagi/learning/`. It organizes learning records on top of ARC-02 memory, ARC-09 orchestration, ARC-10 personal, ARC-11 education, ARC-15 simulation, ARC-16 world model, and ARC-17 cognition. It does not modify any earlier package.

The pipeline is:

experience → lesson analysis → evidenced gaps → learning plan (proposal) → caller-supplied practice attempts → assessment → validation against explicit criteria → learning update proposal → human review → optional skill-record update.

Nothing changes model weights, source code, permissions, or safety policies. `executed` stays false.

## Modules

| Module | Role |
| --- | --- |
| `models.py` | Typed enums and records |
| `provenance.py` | Provenance helper and lifecycle state machine |
| `skills.py` | `SkillGraph` |
| `gaps.py` | `KnowledgeGapDetector` |
| `experience.py` | `ExperienceAnalyzer` |
| `practice.py` | `PracticeEngine` (deterministic and simulated) |
| `assessment.py` | `SkillAssessment` and `SkillValidator` |
| `curriculum.py` | `LearningPlanner` and `EducationLearningAdapter` |
| `adaptation.py` | `AdaptationService`, `TransferService`, `CrossDomainSkillReuse` |
| `integration.py` | Memory, personal, world-model, and cognitive adapters |
| `safety.py` | `LearningSafetyPolicy` |
| `pipeline.py` | `LearningPipeline` |
| `agents.py`, `registration.py` | Eight ARC-01 agents and ARC-09 descriptors |

## Learning lifecycle

States: `IDENTIFIED`, `PROPOSED`, `PLANNED`, `PRACTICING`, `ASSESSING`, `VALIDATING`, `READY_FOR_UPDATE`, `AWAITING_HUMAN_APPROVAL`, `UPDATED`, `REJECTED`, `FAILED`.

`LearningStateMachine.move` raises `ValueError` for any edge outside the table. `UPDATED` is reachable only from `AWAITING_HUMAN_APPROVAL`. `UPDATED`, `REJECTED`, and `FAILED` are terminal.

## Skill model and graph

`Skill` has a type (15 `SkillType` values), a `SkillStatus` (`DECLARED`, `PROPOSED`, `PRACTICED`, `EVALUATED`, `VALIDATED`, `UNKNOWN`), a `SkillLevel`, evidence, a version, provenance, and limitations. Every skill carries the limitation "A recorded skill is not real-world competence."

`SkillGraph` supports `add_skill`, `get_skill`, `add_prerequisite`, `prerequisites`, `dependencies`, `dependents`, `ready_skills`, `order`, and `validate`. It rejects duplicates (case-insensitive), invalid references, self-prerequisites, and cycles; a rejected edge is rolled back. `validate` reports cycles, missing prerequisites, and skills marked `VALIDATED` without passing evidence. The graph never infers mastery: ordering and readiness come only from declared prerequisites and the caller's completed set.

## Knowledge gaps

Gap types: `MISSING_KNOWLEDGE`, `MISSING_SKILL`, `MISSING_EVIDENCE`, `INSUFFICIENT_PRACTICE`, `HIGH_UNCERTAINTY`, `FAILED_VALIDATION`, `MISSING_TOOL`, `MISSING_DOMAIN_CAPABILITY`.

A gap is created only from an explicit task requirement, a skill-graph prerequisite, a supplied experience, or an explicit caller flag (prediction uncertainty, planning failure, unavailable simulation, requested research evidence, missing tool). With no inputs the detector returns an empty list. `confidence` is `None`, and `confidence_basis` says why.

## Experience

`ExperienceRecord` covers task, context, observation, action proposal, simulation, prediction, plan, outcome, evaluation, lesson, constraint violations, prediction error, uncertainty, missing skills and knowledge, and evidence. `ExperienceKind` is exactly one of `OBSERVED`, `SIMULATED`, `PREDICTED`, `SYNTHETIC`, or `UNKNOWN`. A record cannot mix kinds. The cognitive adapter splits one ARC-17 state into separate records per kind.

`ExperienceAnalyzer` extracts eight lesson kinds. A lesson is `EVIDENCED` only for an `OBSERVED` experience with evidence attached; otherwise it is `PROPOSED`. `generalized` is always false: one episode is not a general rule.

## Practice

`PracticeEngine` modes:

- `problem`: compares against a supplied expected answer. No expected answer gives `NOT_EVALUABLE`.
- `code`: runs a caller-supplied Python callable on supplied test cases. No source strings are executed. The score is the pass fraction.
- `research`: citation coverage against required evidence ids.
- `hypothesis`: absolute error against a supplied observation. No observation gives `NOT_EVALUABLE`.
- `simulate`: ARC-15 `MockSimulationBackend`, checked against supplied bounds and targets. Labeled `SIMULATED_PRACTICE`.
- `robot_navigation`: ARC-07 `AStarPlanner` on a grid, then the mock simulation. No physical robot.

A score exists only when it can be computed from supplied data. Otherwise `score` is `None` and `score_status` is `NOT_EVALUABLE`. An unavailable simulation backend produces no evidence.

## Assessment

`SkillAssessment` reports `task_completion`, `constraint_satisfaction`, `error_count`, `evidence_coverage`, and `plan_validity`. Each metric is `COMPUTED`, `SUPPLIED`, or `NOT_EVALUABLE`. Status is `EVALUATED`, `PRACTICED`, `OBSERVED`, `DECLARED`, or `UNKNOWN`. Assessment never returns `VALIDATED`.

## Validation

`SkillValidator` requires at least two evidenced passing attempts (`ValidationCriteria.min_passing_episodes` cannot be below 2). Optional criteria: ground truth match, test suite pass, constraint satisfaction, and observed (non-simulated) evidence. Each must be supplied by the caller. An LLM claim is ignored and noted. A pass on simulated or synthetic evidence carries the limitation "not real-world competence". A validation holds only for the stated criteria.

## Learning plan

`LearningPlanner` expands gaps with skill-graph prerequisites, drops skills already `DECLARED` or `VALIDATED` (unless they are gap subjects), and orders steps topologically. Each step lists prerequisites, a practice task, assessment criteria, validation criteria, and effort only when supplied. Status is `PROPOSAL`, `executed` is false.

`EducationLearningAdapter` wraps ARC-11 `LearningPathPlanner` and `KnowledgeGapAnalyzer`, and converts a `Curriculum` into a `SkillGraph`. It does not re-implement path planning.

## Memory

`LearningMemoryAdapter` writes one episodic record per experience through ARC-02 `UniversalMemory.remember`, with metadata `experience_kind`, `provenance_status`, and `truth=NOT_ASSERTED`. When the experience has a source and evidence, one ARC-02 `Evidence` item is added. Personal context requires persistent consent through the collaboration `ConsentGate`; otherwise `PermissionError`. The existing ARC-02 privacy policy and deduplication still apply.

## Personal

`PersonalLearningAdapter` builds objectives from ARC-10 goals, projects, and learning objectives. Declared preferences go through the collaboration `SafetyPolicy.check_preference`, which rejects sensitive keys. Nothing is inferred about health, politics, or protected characteristics.

## World model

`WorldModelLearningAdapter` writes skills as ARC-16 `CONCEPT` entities with status `PROPOSED`. Only `VALIDATED` skills are labeled `EVIDENCED`; proposed skills are `HYPOTHESIZED`, and the rest are `UNKNOWN`. Prerequisites become `REQUIRES` relations labeled `HYPOTHESIZED`. Simulated and predicted practice results are stored as annotations with `SIMULATED` or `PREDICTED` labels, never as entity properties.

## Cognitive integration

`CognitiveLearningAdapter` reads an ARC-17 `CognitiveState`: observations, simulation, prediction, plan, evaluation, and the ARC-17 `learning_update`. It returns experiences, gaps, and a `LearningProposal` with `applied=false`. ARC-17 is not modified.

## Adaptation

`AdaptationService.propose` accepts only the eight targets: planner strategy, retrieval strategy, skill ordering, practice strategy, domain adapter, tool recommendation, knowledge source, and simulation strategy. It requires evidence and passes the safety policy. Each proposal records reason, evidence, expected benefit, risk, validation requirement, and rollback requirement. Status is `AWAITING_HUMAN_APPROVAL`, `applied=false`. `apply` always raises `PermissionError`.

## Transfer and cross-domain reuse

`TransferService` returns a `SkillTransferProposal` with shared abstraction, assumptions, differences, risks, and validation requirements. `transfer_validated` is false. `CrossDomainSkillReuse` compares per-domain claims about the same skill; disagreements are reported in `conflict` and `selected_winner` stays `None`. It can list domains from the ARC-09 `AgentCapabilityRegistry`.

## Agents

`learning_coordinator_agent`, `learning_gap_agent`, `learning_skill_agent`, `learning_practice_agent`, `learning_assessment_agent`, `learning_validation_agent`, `learning_adaptation_agent`, and `learning_transfer_agent`. They register under domain `learning` and coexist with the evolution, world-model, cognition, collaboration, and engineering agents. Every output has `executed=false`.

## Safety

`LearningSafetyPolicy` rejects unsafe autonomous adaptation, model-weight changes, source-code changes, permission or policy changes, credentials, dangerous physical training, physical robots, malware and exploits, weapons, clinical decisions, hidden personal data, and sensitive-attribute inference. It allows education, simulation, research, engineering, and safe coding practice, knowledge organization, and human-reviewed adaptation proposals.

## Provenance

Every gap, experience, practice attempt, assessment, plan, update, adaptation, and transfer carries a `Provenance` note. A source is `PRESENT` only when it is a non-empty string; otherwise it stays `MISSING`.

## Classifications

| Item | Classification |
| --- | --- |
| Skill graph, gaps, planner, assessment, validator | DETERMINISTIC |
| Simulated practice, robot navigation | SIMULATION ONLY, MOCK |
| Plans, lessons, adaptation, transfer, learning updates | PROPOSAL ONLY |
| Skill-record update after human approval | RECORD UPDATE ONLY (no model, code, or policy change) |

## Known limitations

- Practice attempts are supplied by the caller or computed from deterministic checks. There is no learner model.
- Code practice runs caller-supplied callables in-process; it is not a sandbox.
- Simulated practice uses the ARC-15 mock backend only.
- Validation depends on caller-supplied criteria and flags; the validator cannot check that the flags are true.
- No autonomous lifelong learning, human-level learning, self-improvement, or real-world skill mastery is claimed.
