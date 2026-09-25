# ARC-15 Audit

## Architecture

ARC-15 is an additive package at `src/superagi/evolution/`. It records declared states, runs a deterministic mock transition, makes baseline forecasts, proposes plans, and writes evolution proposals. It does not replace ARC-01 through ARC-14.

The model-based path is:

current state → world model → mock simulation → baseline prediction → plan generation → plan simulation → explicit score → human review.

An evolution cycle stops at `PROPOSAL` or `AWAITING_HUMAN_APPROVAL`. `apply` raises `PermissionError`.

## Design decisions

- Domain-fidelity simulators are descriptors with status `UNAVAILABLE`. The only runnable backend is the deterministic mock.
- Prediction methods are persistence, moving average, linear trend, and an explicit numeric rule. Confidence is a declared heuristic. Measured accuracy stays `NOT_EVALUABLE` unless the caller supplies ground truth.
- Counterfactual output is labeled `COUNTERFACTUAL SIMULATION`, `CAUSAL HYPOTHESIS`, and `NOT CAUSALLY VERIFIED`.
- Plan scores use only caller-supplied weights. The selected name is the lowest explicit sum, not a claim of a best plan.
- Evolution proposals can name a future adapter, evaluation, planner strategy, memory strategy, or tool. They do not edit source, install software, change permissions, or deploy.
- Provenance is recorded only when a source string is supplied. Otherwise `missing` stays true.
- The evolution planning agent is named `evolution_planning_agent` so it can be registered beside ARC-14 `planning_agent`.

## Module map

| Module | Role | Status |
|---|---|---|
| `models.py` | Typed state, simulation, prediction, plan, proposal, and provenance records | IMPLEMENTED |
| `simulation.py` | Mock and unavailable backends | MOCK and UNAVAILABLE |
| `domains.py` | Domain adapter registry for ARC-04 through ARC-14 and extra domains | UNAVAILABLE except `deterministic-mock` |
| `prediction.py` | Baseline `PredictionEngine` | IMPLEMENTED |
| `counterfactual.py` | Paired mock trajectories | MOCK / NOT CAUSALLY VERIFIED |
| `planning.py` | Dependency planner plus `ModelBasedPlanner`, composed with ARC-01 | IMPLEMENTED / PROPOSAL_ONLY |
| `world_model.py` | Entities, relations, observations; optional ARC-02 store | IMPLEMENTED |
| `evolution_cycle.py` | Gap to proposal, human gate, refused apply | PROPOSAL_ONLY |
| `evaluation.py` | Meta-evaluation and proposal review | IMPLEMENTED |
| `safety.py` | Rejects autonomous modification, deployment, credentials, physical and financial execution, weapons, malware | IMPLEMENTED |
| `agents/` | Seven `BaseAgent` wrappers | IMPLEMENTED |
| `registration.py` | ARC-01 and ARC-09 registration | IMPLEMENTED |
| `pipeline.py` | End-to-end proposal flow | PROPOSAL_ONLY |

## Data flow

1. A caller supplies a `SimulationState`, actions, a numeric series, candidate planning actions, and weights.
2. `EvolutionSafetyPolicy` rejects blocked requests before any run.
3. `WorldModel` stores entity names only when a source is present, through `UniversalMemory`.
4. `MockSimulationBackend` adds declared deltas and records the trace.
5. `PredictionEngine` projects the series with the selected baseline.
6. `ModelBasedPlanner` simulates each candidate and scores the supplied criteria.
7. ARC-14 `DecisionSupport` holds the choice as a proposal unless the caller passes human approval. Approval still leaves `executed` false.
8. `EvolutionCycle` records the lifecycle and refuses `apply`.

## Simulation semantics

`MOCK_SIMULATION` means each named delta is added to the matching declared variable. Termination is a step cap or a variable threshold. An unknown variable fails the run with status `FAILED`. `UnavailableSimulationBackend` and non-mock domain adapters return `BACKEND_UNAVAILABLE` and an empty trace. None of these results are physical fidelity. Classification values are `SIMULATION_ONLY` for the pipeline, `MOCK_SIMULATION` for the mock backend, and `BACKEND_UNAVAILABLE` when no backend exists.

## Prediction semantics

Observed inputs stay in the request series. Output points are `PREDICTED`. If the method cannot run, status is `UNKNOWN` and the point list is empty. The confidence basis text says it is a heuristic. `measured_accuracy` is `NOT_EVALUABLE` until `MetaEvaluator.prediction` is given an aligned actual series, in which case the score is mean absolute error on those pairs only.

## Planning semantics

`PlanningEngine` creates an ARC-01 task and core plan, then orders planning actions by satisfied dependencies and preconditions, one ready action at a time, by name. A `max_cost` constraint above the caller limit marks the plan infeasible and keeps the violation visible. `PlanExecutor` can draft the core plan step. No external action is run. `ModelBasedPlanner` reports every term, weight, measured value, and weighted value.

## Counterfactual limitations

The difference is the terminal mock value of the alternative minus the baseline. It assumes the same initial state and the same backend. It is not an identified causal effect, a randomized result, or a verified mechanism. Status text: `NOT CAUSALLY VERIFIED`.

## Self-evolution safety model

Proposals may describe a new tool, skill, planner strategy, adapter, evaluation, or memory strategy. They include expected benefit, risk, a validation requirement, and a rollback requirement. Rollback in this ARC is "do not change the tree." Blocked requests include source modification, autonomous deployment, credentials, unauthorized external actions, irreversible operations, dangerous physical actions, clinical decisions, financial execution, weapons, malware, exploit execution, permission escalation, and hidden personal-data collection. Human approval changes the lifecycle to `PROPOSAL` and still does not apply the change.

## Continuous evolution lifecycle

States: `OBSERVE`, `EVALUATE`, `IDENTIFY_GAP`, `PROPOSE_IMPROVEMENT`, `SIMULATE`, `VERIFY`, `REQUEST_HUMAN_APPROVAL`, then `AWAITING_HUMAN_APPROVAL` or `PROPOSAL`.

`APPLY` is not a lifecycle state. `EvolutionCycle.apply` always raises.

## ARC integrations

- ARC-01: `BaseAgent`, `Task`, `TaskManager`, `Planner`, `PlanExecutor`. New event types were not added to `EventBus`.
- ARC-02: `UniversalMemory.remember` and `ProvenanceStore` when a source is supplied. Evidence quality uses caller text, not a new memory backend.
- ARC-03 and ARC-12: demos call `HypothesisGenerator` and `ExperimentDesigner`. Experiments stay non-executing. No research package was modified.
- ARC-04 through ARC-08, ARC-11, ARC-13, ARC-14: domain descriptors point at those arcs and return `UNAVAILABLE` for real simulators.
- ARC-07: the robot demo uses the existing `AStarPlanner` for a grid walk and separately reports the robotics simulator as `UNAVAILABLE`.
- ARC-09: `register_evolution_agents` writes `AgentDescriptor` records. A test calls `UniversalIntelligenceCoordinator.solve` in computational mode.
- ARC-10: goals remain in the caller statement. This package does not open a second goal store.
- ARC-14: plan review uses `DecisionSupport` and `approve(..., human=True)` only when the caller sets approval. The decision is not an execution.

## Tests

`tests/test_arc15_evolution.py` covers transitions, failure, unavailable backends, prediction baselines, uncertainty, counterfactuals, dependencies, constraint violations, explicit plan scores, world-model memory, missing provenance, the approval gate, safety rejection, agent registration beside ARC-14, ARC-09 discovery, and the four demos.

## Known limitations

- IMPLEMENTED: typed records, mock transitions, baseline forecasts, explicit plan scores, proposal lifecycle, safety rejection, registry descriptors.
- MOCK: `MockSimulationBackend` and any demo trace built from it, including the grid walk.
- UNAVAILABLE: biology, chemistry, neuro, quantum, robotics physics, cybersecurity, education, science dynamics, engineering SPICE, collaboration, economics, space, environment, and social simulators.
- PROPOSAL_ONLY: plans and evolution changes.
- NOT_IMPLEMENTED: learned predictors, measured forecast skill, causal identification, physical simulation, autonomous self-modification, deployment, and applying an approved proposal.

## Future work

A later arc can add an optional adapter behind `DomainSimulationAdapter` that still returns `UNAVAILABLE` when the adapter is not configured. That work is not part of ARC-15. ARC-16 was not started.
