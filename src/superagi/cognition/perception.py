"""Typed ingestion. Predicted and simulated inputs stay labeled."""

from __future__ import annotations

from .models import EpistemicStatus, IngestionResult, Observation, ObservationSource, ProvenanceNote

_LOCKED = {
    ObservationSource.SIMULATION: EpistemicStatus.SIMULATED,
    ObservationSource.PREDICTION: EpistemicStatus.PREDICTED,
}


def note_for(source: str | None, ref: str = "") -> ProvenanceNote:
    cleaned = source.strip() if isinstance(source, str) else ""
    return ProvenanceNote(source=cleaned or None, status="PRESENT" if cleaned else "MISSING", ref_id=ref)


class PerceptionLayer:
    def ingest(self, observations: list[Observation], *, source: str | None) -> IngestionResult:
        kept: list[Observation] = []
        rejected: list[str] = []
        for observation in observations:
            locked = _LOCKED.get(observation.source_kind)
            epistemic = locked or observation.epistemic
            if epistemic == EpistemicStatus.OBSERVED and observation.provenance.status != "PRESENT" and not (source and source.strip()):
                epistemic = EpistemicStatus.UNKNOWN
            provenance = observation.provenance if observation.provenance.status == "PRESENT" else note_for(source, str(observation.id))
            kept.append(observation.model_copy(update={"epistemic": epistemic, "provenance": provenance}))
        return IngestionResult(observations=kept, rejected=rejected, limitations=["EXTERNAL_RESULT is caller-supplied. No live external service is connected.", "SIMULATION and PREDICTION inputs are not rewritten as OBSERVED."])
