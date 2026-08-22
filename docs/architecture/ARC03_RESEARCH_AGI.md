# ARC-03 Research AGI Engine

SuperAGI is an experimental modular AGI research and scientific intelligence
platform. ARC-03 is an evidence-first research engine, not a claim of
autonomous AGI or scientific discovery.

## Architecture

`ResearchQuestion -> ResearchPlan -> Literature -> Evidence -> Assessment -> Synthesis -> Hypothesis -> Critique -> Experiment Proposal -> Verification -> Report`

The pipeline composes ARC-01 `BaseAgent`, `Task`, `AgentContext`, and `EventBus`
with ARC-02 `UniversalMemory`, evidence, knowledge, and provenance. It does not
create a parallel execution or memory system.

## Research Pipeline And Agents

`ResearchTaskDecomposer` creates a finite nine-stage plan. `LiteratureAgent`
uses an explicit `LiteratureProvider`; ARC-03 ships only a controlled local
corpus. `EvidenceAgent` extracts source-grounded excerpts. `SynthesisAgent`
creates findings with evidence IDs. `HypothesisAgent`, `CriticAgent`, and
`ExperimentAgent` produce proposals and critiques. `VerificationAgent` checks
references and structural completeness. No web browsing or physical experiment
execution is included.

## Scientific Integrity

Artifacts distinguish FACT-like source excerpts, EVIDENCE records, INFERENCE in
synthesis, HYPOTHESIS proposals, and UNKNOWN or unsupported gaps. Citations are
never fabricated. Hypotheses remain `PROPOSED`, `SUPPORTED`, `WEAK`,
`CONTRADICTED`, `REJECTED`, or `UNKNOWN` according to explicit evidence links;
generated proposals are not scientific truths.

## Evidence And Provenance

Every extracted evidence item contains claim, source, excerpt, confidence, and
status. Reports carry evidence IDs on findings. ARC-02 provenance records are
retained and artifact snapshots are stored as research memories after a run.

## Experiments And Verification

Experiment proposals classify independent, dependent, control, and confounding
variables and include controls, measurements, failure conditions, safety, and
reproducibility notes. They are plans only. Verification reports missing
evidence, unsupported findings, and incomplete provenance and explicitly warns
that structural verification is not experimental validation.

## Evaluation Metrics

Metrics use transparent ratios for evidence coverage, citation completeness,
provenance completeness, hypothesis testability, contradiction rate,
unsupported claim rate, and reproducibility score. No fabricated accuracy
metric is used.

## Limitations And Extensions

Retrieval is deterministic and local, the corpus is controlled, source quality
is not independently verified, and no real-world experiment is run. Future
providers may implement live literature retrieval, vector or graph search,
reranking, and domain-specific evaluators behind existing interfaces.
