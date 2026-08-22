# ARC-01 Architecture Audit

## Scope

This audit covers the current SuperAGI scaffold before ARC-01 core
implementation. The workspace contains no pre-existing executable application
core or tests to preserve.

## Existing Architecture

- `src/superagi/__init__.py` identifies the platform.
- `src/superagi/integrations/` contains optional upstream integration
  boundaries.
- `src/superagi/integrations/base.py` defines `IntegrationAdapter`,
  `OptionalIntegrationAdapter`, and `ResearchEngineAdapter`.
- `src/superagi/integrations/langgraph/adapter.py` contains the only upstream
  availability probe and workflow placeholder.
- The remaining adapter packages expose dependency-free placeholders.
- `third_party/` contains isolated upstream checkouts and pending-domain
  markers. ARC-01 will not modify those sources.
- `docs/UPSTREAM_PROJECTS.md` and `docs/INTEGRATION_MATRIX.md` record upstream
  provenance and intended integration targets.
- `scripts/` contains guarded clone and metadata-generation utilities.

## Existing Contracts

The integration contracts are intentionally optional and implementation
agnostic. ARC-01 will not duplicate or change them. Core execution contracts
will live under `src/superagi/core/` and depend on abstractions rather than
upstream packages.

## Missing Functionality

- Typed task, plan, execution, event, result, and context models.
- Task, agent, tool, planner, workflow, memory, model, and reasoning engines.
- Event bus and queryable execution traces.
- Permission, approval, risk, and audit controls.
- Safe demo tools and a runnable end-to-end workflow.
- Tests for lifecycle, failure, retries, cancellation, permissions, memory,
  events, traces, and workflow execution.

## Files To Create

- `src/superagi/core/` modules for models, events, tasks, agents, tools,
  planning, reasoning, memory, providers, safety, tracing, workflows, and
  observability.
- `tests/` focused ARC-01 unit and integration tests.
- `examples/core/basic_superagi.py` executable demo.
- `docs/architecture/ARC01_CORE.md` implementation documentation.

## Files To Modify

- `src/superagi/__init__.py` only if public core exports are added.
- `README.md` to describe ARC-01 and the experimental platform scope.

No `third_party/` source, upstream license, or existing adapter implementation
will be modified.
