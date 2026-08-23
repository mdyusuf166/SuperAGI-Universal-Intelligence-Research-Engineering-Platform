# SuperAGI

## ARC-04 — Biomedical Intelligence

Optional, adapter-backed molecular, DNA, chemistry, candidate-prioritization, and controlled biomedical research-pipeline components. Outputs are computational research results, not clinical recommendations or validation.

## ARC-05 — Neurocomputing & Brain Intelligence

Typed, optional-backend computational neuroscience abstractions for simplified neurons, networks, simulations, and spike analysis; not a human brain, consciousness, or clinical BCI system.

SuperAGI is an experimental modular AGI research and scientific intelligence
platform.

## ARC-01

ARC-01 provides the executable core pipeline for tasks, planning, agents,
tools, verification, memory, events, safety, and execution traces. It is
upstream-independent and does not claim human-level AGI.

Run the demo from the repository root:

```powershell
$env:PYTHONPATH = "src"
python examples/core/basic_superagi.py
```

See [docs/architecture/ARC01_CORE.md](docs/architecture/ARC01_CORE.md) and
[docs/architecture/ARC01_AUDIT.md](docs/architecture/ARC01_AUDIT.md).

## ARC-02: Universal Memory & Knowledge Intelligence

ARC-02 adds shared typed memory, document chunking, deterministic lexical
retrieval, a lightweight knowledge graph, evidence, provenance, bounded context
building, privacy, retention, and ARC-01-compatible research workflows. It uses
an in-memory provider only; vector and database backends remain extension
points.

Run the controlled demonstrations:

```powershell
python examples/memory/universal_memory_demo.py
python examples/research/research_context_demo.py
```

See [docs/architecture/ARC02_MEMORY_KNOWLEDGE.md](docs/architecture/ARC02_MEMORY_KNOWLEDGE.md).

## ARC-03: Research AGI Engine

ARC-03 provides an evidence-first research workflow for finite problem
decomposition, controlled literature, evidence assessment, knowledge synthesis,
hypothesis criticism, experiment proposals, verification, reports, provenance,
and transparent evaluation metrics. It does not claim autonomous AGI, fabricate
citations, or execute experiments.

```powershell
python examples/research/research_agi_demo.py
python examples/research/hypothesis_demo.py
```

See [docs/architecture/ARC03_RESEARCH_AGI.md](docs/architecture/ARC03_RESEARCH_AGI.md).
