"""Caller-supplied confidence only. Missing values stay unevaluated."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ConfidenceNote(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: float | None
    basis: str
    measured_accuracy: str = "NOT_EVALUABLE"


def lowest(values: list[float]) -> ConfidenceNote:
    if not values:
        return ConfidenceNote(value=None, basis="No confidence values were supplied.")
    return ConfidenceNote(value=min(values), basis="Minimum of caller-supplied confidence values. Not a measured probability.")
