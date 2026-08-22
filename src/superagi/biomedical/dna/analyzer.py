from __future__ import annotations
from .validation import validate_sequence
from .statistics import gc_content, base_frequency
from .motifs import find_motif

class DNASequenceAnalyzer:
    def validate(self, sequence): return validate_sequence(sequence)
    def _sequence(self, sequence):
        result = self.validate(sequence)
        if not result.valid: raise ValueError("Invalid DNA sequence: " + "; ".join(result.errors))
        return result.normalized_value
    def length(self, sequence): return len(self._sequence(sequence))
    def gc_content(self, sequence): return gc_content(self._sequence(sequence))
    def base_frequency(self, sequence): return base_frequency(self._sequence(sequence))
    def reverse_complement(self, sequence): return self._sequence(sequence).translate(str.maketrans("ACGT", "TGCA"))[::-1]
    def find_motif(self, sequence, motif):
        seq = self._sequence(sequence); checked = self.validate(motif)
        if not checked.valid: raise ValueError("Invalid DNA motif: " + "; ".join(checked.errors))
        return find_motif(seq, checked.normalized_value)
    def compare(self, sequence_a, sequence_b):
        a, b = self._sequence(sequence_a), self._sequence(sequence_b); length = max(len(a), len(b))
        return {"length_a": len(a), "length_b": len(b), "matching_positions": sum(x == y for x, y in zip(a, b)), "identity": sum(x == y for x, y in zip(a, b)) / length if length else None, "status": "COMPUTATIONAL_STATISTIC", "limitations": ["This is a position-wise comparison, not a biological interpretation."]}
