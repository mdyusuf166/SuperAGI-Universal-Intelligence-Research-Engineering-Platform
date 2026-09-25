# ARC-14 Human Collaboration and Personal Intelligence

## Purpose

ARC-14 helps a person and a set of specialized agents organize context, goals, tasks, reviews, and recommendations. It does not replace human judgment. A recommendation is not a decision, a proposal is not execution, and a draft is not an approved action.

## Architecture

The collaboration pipeline is:

Objective → Context → Goals → Roles → Tasks → Dependencies → Agent Coordination → Evidence / Results → Conflict Detection → Review → Recommendations → Human Approval → Final Collaboration Report

The runner stops when safety rejects the objective or when task dependencies contain a cycle. Otherwise it returns a report whose `executed` flag is false. Human approval can mark an action proposal as approved, and the proposal is still not executed by this package.

## Models

Typed records live in `collaboration.models`. They cover a person, consent, preference, constraint, context item, goal, milestone, task, project, role, provenance reference, recommendation, decision, action proposal, review finding, claim, and session. A person record stores only a display name and consent. It has no fields for health, politics, or other protected characteristics.

Collaboration tasks point at an ARC-01 `Task` through `core_task_id`. They add owner, dependencies, evidence, blockers, and completion criteria without a second task engine.

## Consent

`Consent` records granted, denied, or absent state, a scope, and whether persistence was allowed. Persistent storage requires `state=granted`, `persistent=true`, and `"persistent"` in the scope. Denied or absent consent keeps context in the session object only. `PersonalMemoryService.remember` is not called in that case.

Preferences must be `user-declared`. Keys for health, diagnosis, political preference, race, religion, ethnicity, and sexual orientation are rejected.

## Context

`ContextService` keeps at most eight context items and reports when the input was truncated. Session lists keep at most twelve entries each and raise `ValueError` when another item would exceed that bound. Recall uses ARC-02 search and returns at most the requested limit.

## Sessions

`CollaborationSession` tracks the objective, participants, roles, context, goals, tasks, constraints, decisions, recommendations, unresolved questions, provenance, conflicts, and safety state. An automated participant cannot be assigned the decision-maker role.

## Goals

`GoalService` creates goals, records user-supplied progress evidence, and can propose child goals. A proposed child does not change the parent statement. Renaming or completing a goal requires `user_authorized=True`. With persistent consent, `publish` stores the goal through ARC-10 `GoalManager`.

## Tasks

`TaskCoordinator` creates each collaboration task by calling ARC-01 `TaskManager.create_task`. Ordering is a deterministic dependency sort by descending priority and then title. A cycle is returned to the pipeline and fails that stage instead of being ignored.

## Decision support

`DecisionSupport.prepare` returns the question, options, criteria, evidence, assumptions, risks, tradeoffs, a recommendation, uncertainty, and `human_approval_required`. The decision status starts as `PROPOSAL` and `approved` is false. Only `approve(..., human=True)` marks it as a human decision. The text states that the result is not objective correctness.

## Recommendation engine

`RecommendationEngine` chooses the option with the lowest sum of caller-supplied criterion scores, breaking ties by name. The result includes the basis, evidence, assumptions, confidence, uncertainty, limitations, and alternatives. `draft_action` creates a `DRAFT` action proposal with `executed=false`. The engine never starts that action.

## Agents

These agents use ARC-01 `BaseAgent`:

- `CollaborationAgent` runs the pipeline.
- `PlanningAgent` composes a goal with ARC-01 `Planner` and `PlanExecutor`.
- `CoordinationAgent` discovers capabilities and reports conflicts.
- `DecisionSupportAgent` returns a proposal.
- `CommunicationAgent` summarizes only supplied meetings, tasks, updates, participants, and evidence. Missing sections stay `not provided`.
- `ReviewAgent` reports missing requirements, unsupported claims, missing evidence, unresolved conflicts, unclear ownership, ambiguous tasks, missing approval, safety issues, and provenance gaps.

Review severities are `INFO`, `WARNING`, `ERROR`, and `CRITICAL`. Error and critical findings are not accepted.

## Orchestration

`CoordinationService` calls the existing `UniversalIntelligenceCoordinator` and `AgentCapabilityRegistry`. It does not create another orchestrator. Orchestration conflicts and contradictory claims are both returned. `selected_conflict_winner` stays `None`.

Descriptors use the domains `collaboration`, `personal` (as a capability), `planning`, `coordination`, and `decision_support`. Register them with `register_collaboration_agents`.

## Memory

Persistent context is written through ARC-10 `PersonalMemoryService`, which writes to the supplied `UniversalMemory`. That path is used only after persistent consent. Session-only context is not written. Retrieval goes through `UniversalMemory.search`.

## Provenance

`ProvenanceLog.record` stores a reference only when a source string is supplied. A missing source stays missing and the review reports a provenance gap. When storage was persisted, the same event is also appended to the ARC-02 provenance store. The reference can carry evidence, the originating agent, the session, a timestamp, a related task, and a related decision.

## Safety

The safety policy rejects autonomous irreversible actions, unauthorized external actions, hidden personal-data collection, sensitive-attribute inference, credential material, dangerous physical operations, autonomous deployment, and academic cheating. Planning, drafting, summarization, simulation, decision support, research assistance, and project coordination remain allowed. Rejection stops the pipeline on the objective stage.

## ARC integrations

- ARC-01: agents, tasks, and the core planner.
- ARC-02: `UniversalMemory` and provenance records.
- ARC-09: capability registry and `UniversalIntelligenceCoordinator`.
- ARC-10: consent-gated `GoalManager` and `PersonalMemoryService`. Profiles are not copied into a second store.
- ARC-11: study plans use `LearningPathPlanner` and `AcademicIntegrityPolicy`. Exam-answer and cheating requests are rejected.
- ARC-12: research collaboration keeps `FACT`, `EVIDENCE`, `INFERENCE`, `HYPOTHESIS`, `UNKNOWN`, and `CONTRADICTION` separate. Experiment proposals stay non-executing.
- ARC-13: engineering review calls `EngineeringPipeline` and the engineering agent registry. The engineering result remains conceptual and simulation-only.

## Demos

From the repository root, with `PYTHONPATH=src`:

```powershell
$env:PYTHONPATH = "src"
python examples/collaboration/research_team_collaboration.py
python examples/collaboration/student_research_planning.py
python examples/collaboration/engineering_team_design_review.py
```

Demo A drafts a research-team proposal from a user-supplied note. Demo B builds a study plan and waits for human approval. Demo C reviews a conceptual engineering design and does not execute a physical action.

## Limitations

This layer does not know a person's private attributes unless that person types them into an allowed field. It does not decide, send messages, run experiments, grade exams, or operate hardware. Recommendation scores are only as meaningful as the numbers the caller provided. Orchestration conflicts from ARC-09 are listed, including its provenance warnings, and are not resolved here. Bounded lists drop nothing silently: context is truncated with a flag, and a full session list raises.
