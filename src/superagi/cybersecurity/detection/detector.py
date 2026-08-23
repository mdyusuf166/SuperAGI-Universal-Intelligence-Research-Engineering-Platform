from ..models import SecurityAlert
class DetectionEngine:
 def detect(self,events):
  failed=[e for e in events if e.event_type=="failed_login"]
  alerts=[]
  if len(failed)>=3:alerts.append(SecurityAlert(rule_id="repeated_failed_login",severity="medium",event_ids=[e.id for e in failed],reason="Repeated failed login events in local synthetic input."))
  for e in events:
   if e.event_type in {"privilege_change","service_start","configuration_violation"}:alerts.append(SecurityAlert(rule_id=e.event_type,severity="high",event_ids=[e.id],reason="Deterministic local rule matched."))
  return alerts
