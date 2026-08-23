from collections import Counter
class LogAnalyzer:
 def frequency(self,events):return Counter(e.event_type for e in events)
 def severity_distribution(self,events):return Counter(e.severity for e in events)
 def timeline(self,events):return sorted(events,key=lambda e:e.timestamp)
