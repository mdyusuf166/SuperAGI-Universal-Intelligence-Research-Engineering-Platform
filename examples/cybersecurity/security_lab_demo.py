from superagi.cybersecurity import SecurityEvent,DetectionEngine
from superagi.cybersecurity.safety import CyberSafetyPolicy
events=[SecurityEvent(source="local-lab",event_type="failed_login") for _ in range(3)]+[SecurityEvent(source="local-lab",event_type="privilege_change")]
print("SUPERAGI ARC-08 CYBERSECURITY DEMO\nEnvironment: LOCAL LAB ONLY\nAlerts:",DetectionEngine().detect(events),"\nSafety:",CyberSafetyPolicy().assess("analyze synthetic logs"))
