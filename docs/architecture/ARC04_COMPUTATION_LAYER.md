# ARC-04 Computation Layer

ARC-04 adds composable molecular, DNA, chemistry, and computational candidate-ranking utilities. Molecular functions use `RDKitAdapter`; property prediction routes through injected DeepChem or Chemprop adapters. These are optional dependencies and return structured unavailable results rather than fabricated outputs.

DNA utilities validate only the A/C/G/T alphabet and provide computational statistics, exact motif matches, and simple position-wise comparison. They do not infer biological, clinical, or disease significance.

Artifacts retain source, status, limitations, and existing model provenance fields. They can be stored with `UniversalMemory.remember`; no separate store is introduced. Core event types cover ARC-04 activity and use the existing `EventBus`/`Event` contract. All molecular descriptors, similarity calculations, and predictions are computational results, not proof, experimental validation, approval, diagnosis, or treatment recommendations.
