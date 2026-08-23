from superagi.cybersecurity import Asset,SecurityEvent,AssetInventory,DetectionEngine,RiskEngine,CodeSecurityAnalyzer
from superagi.cybersecurity.safety import CyberSafetyPolicy
def test_defensive_local_analysis():
 a=Asset(name="lab",asset_type="server");assert AssetInventory().register(a)==a
 alerts=DetectionEngine().detect([SecurityEvent(source="lab",event_type="failed_login") for _ in range(3)]);assert alerts[0].rule_id=="repeated_failed_login"
 assert RiskEngine().assess(a,1,1).risk_score==.5;assert len(CodeSecurityAnalyzer().analyze("password='x'; eval('x')"))==2;assert not CyberSafetyPolicy().assess("exploit host").allowed
