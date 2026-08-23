from __future__ import annotations
class CandidateRanking:
    def rank(self, candidates, criteria):
        def score(candidate): return sum(float(candidate.molecular_properties.get(key, 0)) * weight for key, weight in criteria.items())
        ranked = sorted(candidates, key=score, reverse=True)
        return [{"candidate": candidate, "score": score(candidate), "status": "PROPOSED CANDIDATE"} for candidate in ranked]
