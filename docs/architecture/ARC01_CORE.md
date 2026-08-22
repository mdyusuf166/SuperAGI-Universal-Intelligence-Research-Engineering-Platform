# ARC-01 SuperAGI Core

SuperAGI is an experimental modular AGI research and scientific intelligence
platform. ARC-01 provides the executable, upstream-independent pipeline:

`Task -> Context -> Planner -> Plan -> Agent -> Tool -> Observation -> Verification -> Result -> Memory -> Trace`

## Architecture

Core contracts live under `src/superagi/core/`. Optional upstream projects stay
under `third_party/` and are reached only through integration adapters.

## Lifecycles

Tasks move from `CREATED` to `QUEUED` to `RUNNING` and then `COMPLETED`.
Failures move to `FAILED`; queued or running tasks may become `CANCELLED`. Each
transition emits an event.

Agents expose `BaseAgent.run(task, context)` and carry typed metadata. The
registry rejects duplicate names. Tools are registered independently and are
identified by UUIDs in traces.

## Planning

`Planner` creates typed plans. `PlanExecutor` resolves dependencies, runs ready
independent steps concurrently, and supports retries, timeouts, and
cancellation. Recursive unrestricted planning is not part of ARC-01.

## Reasoning And Verification

`ReasoningEngine` returns concise structured reports containing assumptions,
evidence, decisions, confidence, limitations, and verification status. Private
chain-of-thought is neither captured nor exposed.

## Memory And Providers

`MemoryProvider` is the persistence boundary. `InMemoryMemoryProvider` supports
working, episodic, semantic, and procedural memories. Vector, relational,
Redis, and graph implementations are extension points for later arcs.

`ModelProvider` and `MockModelProvider` isolate model access. No provider or API
key is hardcoded.

## Events And Trace

`EventBus` records typed task, plan, agent, tool, memory, and verification
events. `ExecutionTrace.events_for_task()` reconstructs a run by task ID and is
the source used by the basic demo.

## Safety And Observability

`PermissionManager` requires explicit approval for high-risk and critical tools.
The demo tools are read-only: arithmetic, text statistics, and sandboxed file
reading. `AuditLogger` redacts common credential field names. Operational
records can carry task, agent, workflow, event, status, duration, and error
metadata without storing secrets.

## Extension Points

Future work can add adapters, model providers, memory backends, tool
implementations, workflow types, and dashboard consumers without changing the
core contracts. Upstream source and attribution remain outside the runtime
package.
