"""Counterfactual trajectories from declared alternatives. Not causal identification."""

from __future__ import annotations

from .models import CounterfactualResult, DifferenceItem, SimulationScenario
from .simulation import SimulationBackend


class CounterfactualEngine:
    def __init__(self, backend: SimulationBackend) -> None:
        self.backend = backend

    def compare(self, baseline: SimulationScenario, alternative: SimulationScenario, *, assumptions: list[str] | None = None) -> CounterfactualResult:
        base = self.backend.run(baseline)
        other = self.backend.run(alternative)
        differences: list[DifferenceItem] = []
        if base.trace and other.trace:
            left = {item.name: item.value for item in base.trace[-1].variables}
            right = {item.name: item.value for item in other.trace[-1].variables}
            for name in left:
                if name in right:
                    differences.append(DifferenceItem(variable=name, baseline=left[name], counterfactual=right[name], delta=right[name] - left[name]))
        return CounterfactualResult(
            baseline=base,
            counterfactual=other,
            differences=differences,
            assumptions=assumptions or ["Both trajectories use the same declared initial state and the selected backend."],
            uncertainty="The numeric delta is a simulation difference, not an identified causal effect.",
            limitations=["COUNTERFACTUAL SIMULATION. CAUSAL HYPOTHESIS. NOT CAUSALLY VERIFIED."],
            provenance=baseline.provenance,
        )
