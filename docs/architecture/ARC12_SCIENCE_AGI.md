# ARC-12 Scientific Intelligence

ARC-12 is a deterministic, proposal-only scientific reasoning composition layer. It does not claim autonomous discovery, AGI-level intelligence, verified results, laboratory validation, medical advice, or hardware control.

`ScientificQuestion` flows through domain classification, local knowledge synthesis, unknown detection, proposed-hypothesis generation, critique, prediction, non-executing experiment design, simulation proposal, verification summary, and a `ScientificReport`. Facts, evidence, inferences, hypotheses, unknowns, and contradictions are distinct typed labels; inference is never silently converted into fact.

Evidence and provenance are references compatible with ARC-02 `UniversalMemory`, `Evidence`, and `ProvenanceRecord`. Reports carry these references so unsupported conclusions remain identifiable. Hypotheses are always labelled **PROPOSED HYPOTHESIS** and use only PROPOSED, SUPPORTED, CONTRADICTED, or UNTESTED lifecycle states—not proven.

Simulation uses the `SimulationBackend` boundary. Unavailable physics, chemistry, neuroscience, quantum, and robotics backends return `UNAVAILABLE`; no real backend is silently replaced. The included deterministic mock is for tests only.

Cross-domain plans express domain contributions and dependencies, supporting conceptual combinations such as quantum computing and molecular modelling. ARC-09 can discover `ScienceAgent` through its ordinary capability registry. ARC-10/11 context may be passed explicitly, but ARC-12 never automatically stores personal information.

The safety policy permits theoretical reasoning, literature synthesis, computational analysis, simulations, proposals, and education. It rejects physical/laboratory execution, harmful procedures, clinical claims/actions, autonomous hardware, and irreversible external actions. Future extensions may add reviewed adapters, richer literature retrieval, and validated domain simulators behind the same boundaries.
