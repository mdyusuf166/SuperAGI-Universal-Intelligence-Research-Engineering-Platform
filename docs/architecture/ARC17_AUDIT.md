# ARC-17 Audit

## Architecture

ARC-17 adds `src/superagi/cognition/`. It is an orchestration loop over ARC-01 through ARC-16. It does not replace memory, the world model, simulation, prediction, planning, decision support, or evolution.

One cycle is:

ingest → bounded context → world-model slice → structured reasoning → optional simulation → optional prediction → plan proposal → decision support → action proposal → safety review → human gate → caller-supplied observation → structural evaluation → learning proposal → evolution proposal.

`executed` stays false. External, physical, and irreversible actions are not run.

## Cognitive lifecycle

States: `CREATED`, `INGESTING`, `CONTEXT_READY`, `REASONING`, `SIMULATING`, `PREDICTING`, `PLANNING`, `DECISION_REVIEW`, `ACTION_PROPOSED`, `AWAITING_HUMAN_APPROVAL`, `OBSERVING`, `EVALUATING`, `LEARNING`, `EVOLUTION_REVIEW`, `COMPLETED`, `FAILED`, `CANCELLED`.

`CognitiveStateMachine.move` raises `ValueError` for an edge that is not in the table. `cancel()` and a failed safety review stop the cycle. A failed stage does not mark later stages as successful.

If approval is required and the caller does not set `human_approved`, the lifecycle stops at `AWAITING_HUMAN_APPROVAL`. The feedback status is `NOT_EXECUTED` even if the caller supplied a success label. An approved proposal is `APPROVED` and still `executed=false`. `EXECUTED` is not produced.

## State machine

`CognitiveState` holds the task id, goal, observations, evidence refs, memory refs, world-model refs, reasoning, simulation, prediction, plan, decision, action proposals, evaluation, learning update, evolution record, provenance, safety report, and lifecycle history. Those fields are typed models.

## Data flow

1. ARC-01 `TaskManager` creates the task and moves it queued → running.
2. Existing safety policies review the goal text.
3. Observations are ingested with epistemic locks for simulation and prediction.
4. Context keeps at most four items in each list.
5. ARC-15 simulation and prediction run only when requested.
6. ARC-15 planning returns a proposal.
7. ARC-14 `DecisionSupport` records criteria, evidence, assumptions, risks, and tradeoffs.
8. The action proposal stays unexecuted.
9. A caller-supplied outcome is stored as synthetic feedback.
10. Evaluation, a learning proposal, and an evolution proposal are attached.
11. If a source and a memory store are present, one summary is written through ARC-02. A predicted value can be annotated on an existing ARC-16 entity as `PREDICTED`.

## Context construction

`CognitiveContextBuilder` reads ARC-02 search hits, ARC-16 entities and relations, caller constraints, research notes, and an ARC-10 goal title when the route is personal. It does not copy a full store. Truncation is reported.

## Reasoning contract

`BoundedReasoner` stores claims, inferences, unknowns, contradictions, assumptions, a confidence note, and limitations. Inferences are `INFERRED`. A generated science hypothesis is `HYPOTHESIZED`. Neither is stored as an observed fact. No chain-of-thought text is kept.

## Simulation integration

`CognitiveSimulationAdapter` calls the ARC-16 simulation adapter, which calls the ARC-15 backend. The mock backend returns `MOCK_SIMULATION` and epistemic `SIMULATED`. `UnavailableSimulationBackend` returns `SIMULATION_BACKEND_UNAVAILABLE` and epistemic `UNKNOWN`. No substitute trajectory is invented. The plan that follows does not treat that result as a successful simulation.

## Prediction integration

`CognitivePredictionAdapter` calls ARC-15 `PredictionEngine`. Points stay `PREDICTED`. Confidence is the engine's declared heuristic. `measured_accuracy` stays `NOT_EVALUABLE`.

## Planning integration

`CognitivePlanningAdapter` calls ARC-15 `PlanningEngine` and, when declared signals exist, `ModelBasedPlanner`. Status is `PROPOSAL`. `executed` is false. The comparison basis is the caller-supplied weight text from ARC-15.

## Decision integration

`CognitiveDecisionAdapter` calls ARC-14 `DecisionSupport.prepare`. Options, criteria, evidence, assumptions, risks, and tradeoffs are copied onto `DecisionView`. `approve(..., human=True)` runs only when the caller sets `human_approved`. The view's `executed` flag stays false.

## Safety architecture

`CognitiveSafetyGate` calls, and does not replace:

- ARC-07 `RoboticsSafetyPolicy` for physical-action wording
- ARC-08 `CyberSafetyPolicy`
- ARC-11 `AcademicIntegrityPolicy`
- ARC-13 `EngineeringSafetyPolicy`
- ARC-14 collaboration `SafetyPolicy`
- ARC-15 `EvolutionSafetyPolicy`
- ARC-16 `WorldModelSafetyPolicy`
- ARC-12 `ScientificSafetyPolicy`
- ARC-05 `assess_neuro_request`
- ARC-10 is recorded as memory-permission required; personal memory is not written by the cycle

A rejected finding sets the cycle to `FAILED` before planning.

## Feedback loop

Outcomes are `OBSERVED_SUCCESS`, `OBSERVED_FAILURE`, `OBSERVED_PARTIAL`, `UNKNOWN_OUTCOME`, or `NOT_EXECUTED`. Unapproved cycles force `NOT_EXECUTED`. Approved cycles keep a caller-supplied label and mark it synthetic. No real-world outcome is fabricated.

## Learning proposal

`LearningUpdateProposal.applied` is false. `apply` raises `PermissionError`. Gaps name missing evidence, unknowns, prediction failure, or an unavailable simulator. Weights, source, permissions, and policies are not changed.

## Evolution proposal

`EvolutionProposalService` calls ARC-15 `EvolutionCycle.propose` with `approved=False`. The record lifecycle is `AWAITING_HUMAN_APPROVAL`, `applied` is false, and the change is not installed.

## Cross-domain routing

`CognitiveRouter` matches a short capability list to ARC packages. One match is reported as a single capability match. Several matches set `selected_winner` to null and keep every contribution. No match points at ARC-09 orchestration without choosing a domain winner.

## Provenance

Each cycle stage has a `ProvenanceNote`. Status is `PRESENT` only when the caller supplied a non-empty source. Otherwise it is `MISSING`.

## Event trace

`CognitiveTrace` stores the named cognitive events. The same names are copied into ARC-01 `Event.metadata["cognitive_event"]` using existing `EventType` values. `EventType` was not extended. Hidden reasoning text is not included.

## Failure handling

`cancel()` moves a non-terminal cycle to `CANCELLED` and cancels the ARC-01 task. Safety rejection and invalid use of a failed dependency produce `FAILED` with a reason. Unavailable simulation remains unavailable.

## Tests

`tests/test_arc17_cognition.py` covers lifecycle edges, cancellation, ingestion locks, context bounds, contradictions, unknowns, missing provenance, simulation, prediction, planning, decisions, memory, world-model annotations, events, the approval gate, safety rejection, routing, learning and evolution refusal, agent registration, and five demos.

## Limitations

- IMPLEMENTED: typed cycle, validated lifecycle, bounded context, structured reasoning, safety composition, proposals, traces, and routing.
- MOCK: ARC-15 mock simulation when that backend is selected.
- UNAVAILABLE: an explicit unavailable simulation backend, and ARC-16 domain knowledge bases used by the robot demo.
- PROPOSAL_ONLY: plans, decisions, actions, learning updates.
- AWAITING_HUMAN_APPROVAL: action proposals that require approval, and every evolution record from this cycle.
- NOT_IMPLEMENTED: external execution, physical control, learned updates, accuracy scores, causal proof, and any claim of general intelligence.

## Future research

A later arc can attach optional domain workers behind the router while still returning unavailable when a worker is absent. That work is not part of ARC-17. ARC-18 was not started.
