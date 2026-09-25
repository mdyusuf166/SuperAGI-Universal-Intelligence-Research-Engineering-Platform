"""Caller-supplied confidence. This is not a measured probability."""

from __future__ import annotations

from .models import UncertaintyReport


def combine(confidences: list[float]) -> UncertaintyReport:
    if not confidences:
        return UncertaintyReport(confidence=None, basis="No confidence values were supplied.", measured_accuracy="NOT_EVALUABLE")
    lowest = min(confidences)
    return UncertaintyReport(confidence=lowest, basis="Minimum of caller-supplied confidence values. Not a measured probability.", measured_accuracy="NOT_EVALUABLE")
