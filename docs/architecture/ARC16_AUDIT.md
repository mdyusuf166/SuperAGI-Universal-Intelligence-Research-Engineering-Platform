# ARC-16 Audit

## Architecture

ARC-16 adds `src/superagi/world_model/`. It is a typed graph and timeline for entities, relations, states, and evidence. ARC-02 remains the memory store. ARC-15 remains the simulation, prediction, and planning implementation. This package does not replace either one.

The pipeline order is:

input → entity registration → relation registration → state construction → temporal update → evidence linking → contradiction check → query or bounded reasoning → provenance → report.

Nothing in the pipeline is executed outside the process.

## Design decisions

- Epistemic labels are `OBSERVED`, `EVIDENCED`, `INFERRED`, `HYPOTHESIZED`, `PREDICTED`, `SIMULATED`, `UNKNOWN`, and `CONTRADICTED`.
- `CAUSES_HYPOTHESIS` is stored as `HYPOTHESIZED` with verification `NOT CAUSALLY VERIFIED`. A caller label of `OBSERVED` or `SUPPORTED` is not kept for that relation.
- `CORRELATED_WITH` is stored as correlation, with verification `NOT CAUSATION`.
- Predicted and simulated values are annotations. They do not replace an observed property.
- Contradictory observed or evidenced values are both kept, marked `CONTRADICTED`, and left `UNRESOLVED` until the caller supplies an evidence reference and a rule. The other value is not deleted.
- Missing sources stay `provenance_status=MISSING`. The adapter does not invent a source.
- Domain knowledge bases are descriptors with status `UNAVAILABLE`. Caller-supplied `DeclaredRecord` rows can still be mapped, and an observed row without a source is stored as `UNKNOWN`.
- The ARC-16 world-model agent is registered as `universal_world_model_agent` so it can sit beside ARC-15 `world_model_agent`.

## World model schema

| Record | Role | Status |
|---|---|---|
| `WorldEntity`, `EntityType`, `EntityProperty`, `EntityState` | Typed things and properties | IMPLEMENTED |
| `WorldRelation`, `RelationType` | Typed edges with evidence, confidence, status, provenance | IMPLEMENTED |
| `WorldEvent`, `WorldObservation`, `WorldAction` | Events, readings, and named actions | IMPLEMENTED |
| `WorldConstraint`, `WorldGoal` | Caller-supplied limits and goals | IMPLEMENTED / PROPOSAL_ONLY |
| `WorldState`, `WorldSnapshot`, `WorldTransition` | Labeled state and the step between two snapshots | IMPLEMENTED |
| `Conflict` | Both values, evidence, provenance, resolution status | IMPLEMENTED |
| `ProvenanceRef` | Source present or `MISSING` | IMPLEMENTED |

Entity status is `KNOWN`, `OBSERVED`, `PROPOSED`, or `UNKNOWN`. A proposed entity is not a verified entity.

## Knowledge graph

`KnowledgeGraph` supports `add_entity`, `get_entity`, `update_entity`, `add_relation`, `remove_relation`, `get_relations`, `neighbors`, `path`, `subgraph`, and `validate`.

Writes are deterministic. Neighbors and paths use entity name, then id. Duplicate names of the same type are rejected. Duplicate edges are rejected. Self-links are rejected except `RELATED_TO`. Dangling endpoints are rejected.

`validate` reports duplicate entities, dangling endpoints, prohibited self-links, duplicate edges, observed entities with no source, and a causal hypothesis that is not labeled `HYPOTHESIZED` / `NOT CAUSALLY VERIFIED`.

## Temporal model

`Timeline` stores snapshots in insertion order. `state_at(step)` returns the latest snapshot whose step is less than or equal to the query. It returns nothing when no snapshot exists.

`order` reports `BEFORE`, `AFTER`, or `DURING` for two steps. `intervals` reports `BEFORE`, `AFTER`, `DURING`, or `OVERLAP`. This is an in-memory list, not a temporal database.

## State transitions

`OBSERVED_TRANSITION`, `SIMULATED_TRANSITION`, and `PREDICTED_TRANSITION` are separate. A simulated snapshot cannot be attached with an observed transition. The same rule holds for predicted snapshots. Comparison of two states keeps each side's epistemic label.

## Memory integration

`MemoryAdapter` reads an ARC-02 `Evidence` or `MemoryRecord` into a `CONCEPT` entity with status `PROPOSED`. A non-empty source becomes `EVIDENCED` and `PRESENT`. An empty source becomes `UNKNOWN` and `MISSING`. `remember` writes through `UniversalMemory` only when a source is present. ARC-02 is not replaced.

## Simulation integration

`SimulationAdapter` calls the ARC-15 backend. The mock backend records a `SIMULATED` annotation and a `SIMULATED_TRANSITION` classified `MOCK_SIMULATION`. `UnavailableSimulationBackend` returns `BACKEND_UNAVAILABLE` and stores no snapshot. Simulated numbers are not copied onto observed properties.

## Prediction integration

`PredictionAdapter` calls ARC-15 `PredictionEngine`. A successful baseline point is stored as `PREDICTED` with the engine's declared heuristic confidence. Measured accuracy remains `NOT_EVALUABLE` inside that engine. The point is not stored as an observed fact. An unknown forecast is not stored.

## Planning integration

`PlanningAdapter` calls ARC-15 `PlanningEngine` and `ModelBasedPlanner`. The world model supplies the goal text, constraints, and declared numbers. The result status is `PROPOSAL` and `executed` is false. No external action is run.

## Contradiction model

Two different evidenced or observed values for the same property open a `Conflict`. A `SUPPORTS` edge and a `CONTRADICTS` edge between the same pair do the same. Resolution stays `UNRESOLVED` unless `resolve_conflict` receives both a rule and an evidence reference that is already on the conflict. Queries for a property skip `CONTRADICTED` values so neither side is returned as the settled reading.

## Provenance

`ProvenanceRef.status` is `PRESENT` only when `source` is non-empty. `find_provenance_chain` returns the entity link and relation links, including missing ones. `ProvenanceLog` writes an ARC-02 `ProvenanceRecord` only when a source and a memory object are both supplied.

## Safety

`WorldModelSafetyPolicy` rejects hidden personal-data collection, sensitive-attribute inference, unauthorized surveillance, credentials, unauthorized external actions, clinical decisions, financial execution, weapons, malware, exploit execution, and autonomous physical control. Research modeling, simulation, planning, knowledge organization, evidence analysis, engineering models, education models, and scientific hypotheses are allowed. Rejection raises `PermissionError` or returns a failed pipeline report with `executed` false.

## Domain adapters

`WorldModelDomainRegistry` lists biomedical, neuro, quantum, robotics, cybersecurity, education, science, engineering, personal, collaboration, environment, and space. `import_backend` returns `UNAVAILABLE` and no entities. `map_declared` maps caller-supplied records into the common entity shape. That mapping is not a domain knowledge base.

## Agents

Registered on ARC-01 `AgentRegistry` and ARC-09 `AgentCapabilityRegistry`, domain `world_model`:

- `universal_world_model_agent`
- `knowledge_graph_agent`
- `world_query_agent`
- `conflict_detection_agent`
- `world_state_agent`

They return `executed: false`. ARC-09 orchestration code was not copied or modified.

## Tests

`tests/test_arc16_world_model.py` covers model validation, entities, relations, traversal, paths, duplicates, invalid references, self-links, temporal order, transition labels, prediction, simulation, unavailable simulation, planning, memory, provenance, evidence links, contradictions, queries, domains, agents, safety, unknown labels, inference labels, the pipeline, and four demos.

## Limitations

- IMPLEMENTED: typed graph, queries, bounded transitive closure for `PART_OF`, `DEPENDS_ON`, and `PRECEDES`, contradiction records, provenance gaps, safety rejection, and the pipeline report.
- MOCK: ARC-15 mock simulation used by the simulation adapter and the robot demo.
- UNAVAILABLE: every domain knowledge-base backend listed above.
- INFERRED: only explicit transitive edges. They are not observations.
- PREDICTED: ARC-15 baseline forecasts only. No learned model and no accuracy claim.
- SIMULATED: mock arithmetic on declared variables. Not physical fidelity.
- PROPOSAL_ONLY: plans and goals.
- NOT_IMPLEMENTED: a temporal database, domain knowledge bases, causal identification, learned prediction, automatic conflict winners, and any promotion of simulated or predicted state into observed fact.

## Future research

A later arc can attach an optional domain loader that still returns `UNAVAILABLE` when the loader is absent. That work is not part of ARC-16. ARC-17 was not started.
