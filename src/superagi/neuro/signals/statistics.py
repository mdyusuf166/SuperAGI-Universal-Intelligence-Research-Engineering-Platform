from __future__ import annotations
class SpikeTrainAnalyzer:
    def spike_count(self, train): return len(train.timestamps)
    def firing_rate(self, train): return len(train.timestamps)/train.duration
    def inter_spike_intervals(self, train): return [b-a for a,b in zip(train.timestamps,train.timestamps[1:])]
    def population_rate(self, trains): return sum(len(t.timestamps) for t in trains)/max((t.duration for t in trains),default=1.0)
