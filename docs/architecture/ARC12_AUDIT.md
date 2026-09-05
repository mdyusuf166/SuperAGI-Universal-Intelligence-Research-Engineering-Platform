# ARC-12 Audit

ARC-12 was audited against ARC-01 through ARC-11 before implementation. It adds only `superagi.science`; it does not alter previous APIs or third-party code.

- **Reusable APIs:** ARC-01 `BaseAgent`/typed task results; ARC-02 `UniversalMemory`; ARC-03 proposal-oriented research artifacts; ARC-09 capability registry/router; ARC-10/11 explicit context providers.
- **Scientific artifacts:** ARC-04 biomedical computation, ARC-05 neuro simulation, ARC-06 quantum circuits, ARC-07 robot simulation, and ARC-03 hypotheses/experiments are reusable only through their existing safe boundaries.
- **Evidence/provenance:** ARC-02 `Evidence`, `ProvenanceRecord`, `Document`, chunks, and knowledge graph remain the authoritative interfaces. ARC-12 stores references, not unverifiable citations.
- **Simulation interfaces:** existing optional simulation adapters remain optional. ARC-12 has an unavailable response and a deterministic mock restricted to tests.
- **Domain adapters:** biomedical, neuro, quantum, robotics, and research packages are composition candidates; no adapter is invoked for physical action.
- **Safety boundaries:** ARC-09 denies physical/external execution; ARC-10 consent rules remain intact; ARC-12 denies laboratory, harmful biological/chemical, clinical, and autonomous-hardware requests.
- **Extension points:** `SimulationBackend`, domain classifier, `KnowledgeSynthesizer`, typed agents, and the capability registry.
- **Compatibility risks:** enum/string boundaries, optional dependencies, and accidental persistence of personal data. ARC-12 accepts explicit references only and never auto-stores personal context.
