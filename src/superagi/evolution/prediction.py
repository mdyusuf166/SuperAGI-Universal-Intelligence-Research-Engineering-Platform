"""Baseline forecasts. Confidence here is a declared heuristic, not measured accuracy."""

from __future__ import annotations

from .models import (
    EpistemicStatus,
    ForecastPoint,
    PredictionConfidence,
    PredictionMethod,
    PredictionOutput,
    PredictionRequest,
    PredictionUncertainty,
)


def _heuristic(method: PredictionMethod, count: int) -> PredictionConfidence:
    declared = {PredictionMethod.PERSISTENCE: 0.3, PredictionMethod.MOVING_AVERAGE: 0.35, PredictionMethod.LINEAR_TREND: 0.35, PredictionMethod.RULE_BASED: 0.25}
    return PredictionConfidence(value=declared[method] if count else 0.0, basis=f"Declared heuristic for {method.value} with {count} observed points. Not a measured accuracy.", measured_accuracy="NOT_EVALUABLE")


class PredictionEngine:
    def predict(self, request: PredictionRequest) -> PredictionOutput:
        series = list(request.series)
        horizon = request.horizon.steps
        limitations = ["No machine-learning model is used. This is a deterministic baseline."]
        assumptions = list(request.assumptions) or ["Future values follow the declared baseline rule."]
        uncertainty = PredictionUncertainty(statement="No holdout error was computed.", status=EpistemicStatus.UNKNOWN)
        if request.method == PredictionMethod.LINEAR_TREND and len(series) < 2:
            return self._unknown(request, "Linear trend needs at least two observed points.")
        if request.method == PredictionMethod.RULE_BASED and request.rule_delta is None:
            return self._unknown(request, "Rule-based prediction needs an explicit rule_delta.")
        if not series:
            return self._unknown(request, "No observed series was supplied.")
        values = self._project(series, horizon, request.method, request.rule_delta)
        start = len(series)
        points = [ForecastPoint(step=start + offset, value=value, status=EpistemicStatus.PREDICTED) for offset, value in enumerate(values)]
        return PredictionOutput(points=points, method=request.method, horizon=horizon, confidence=_heuristic(request.method, len(series)), uncertainty=uncertainty, assumptions=assumptions, limitations=limitations, evidence=list(request.evidence), provenance=request.provenance, status=EpistemicStatus.PREDICTED)

    def _project(self, series: list[float], horizon: int, method: PredictionMethod, rule_delta: float | None) -> list[float]:
        if method == PredictionMethod.PERSISTENCE:
            return [series[-1]] * horizon
        if method == PredictionMethod.MOVING_AVERAGE:
            average = sum(series) / len(series)
            return [average] * horizon
        if method == PredictionMethod.RULE_BASED:
            assert rule_delta is not None
            return [series[-1] + rule_delta * (index + 1) for index in range(horizon)]
        count = len(series)
        mean_x = (count - 1) / 2
        mean_y = sum(series) / count
        variance = sum((index - mean_x) ** 2 for index in range(count))
        slope = 0.0 if variance == 0 else sum((index - mean_x) * (value - mean_y) for index, value in enumerate(series)) / variance
        intercept = mean_y - slope * mean_x
        return [intercept + slope * (count + index) for index in range(horizon)]

    def _unknown(self, request: PredictionRequest, reason: str) -> PredictionOutput:
        return PredictionOutput(points=[], method=request.method, horizon=request.horizon.steps, confidence=PredictionConfidence(value=0.0, basis=reason, measured_accuracy="NOT_EVALUABLE"), uncertainty=PredictionUncertainty(statement=reason, status=EpistemicStatus.UNKNOWN), assumptions=list(request.assumptions), limitations=[reason], evidence=list(request.evidence), provenance=request.provenance, status=EpistemicStatus.UNKNOWN)
