"""Safety gate that calls existing policies. It does not replace them."""

from __future__ import annotations

from superagi.collaboration.safety import SafetyPolicy as CollaborationSafetyPolicy
from superagi.cybersecurity.safety.policies import CyberSafetyPolicy
from superagi.education.services import AcademicIntegrityPolicy
from superagi.engineering.services import EngineeringSafetyPolicy
from superagi.evolution.safety import EvolutionSafetyPolicy
from superagi.neuro.safety.policies import assess_neuro_request
from superagi.robotics.models import RobotCommand
from superagi.robotics.safety.policies import RoboticsSafetyPolicy
from superagi.science.safety import ScientificSafetyPolicy
from superagi.world_model.validation import WorldModelSafetyPolicy

from .models import SafetyFinding, SafetyReport

_PHYSICAL = ("physical action", "real robot", "actuator command", "dangerous physical", "autonomous physical")


def _finding(policy: str, allowed: bool, reasons, mode: str) -> SafetyFinding:
    return SafetyFinding(policy=policy, allowed=allowed, reasons=[str(item) for item in reasons], mode=mode)


class CognitiveSafetyGate:
    def review(self, text: str) -> SafetyReport:
        findings = []
        physical = any(item in text.casefold() for item in _PHYSICAL)
        robot = RoboticsSafetyPolicy().assess(RobotCommand(command_type="cognitive-proposal", requires_approval=physical), approved=False)
        findings.append(_finding("ARC-07", robot.allowed, [robot.reason] if not robot.allowed else [], robot.mode))
        cyber = CyberSafetyPolicy().assess(text)
        findings.append(_finding("ARC-08", cyber.allowed, [cyber.reason] if not cyber.allowed else [], cyber.mode))
        education = AcademicIntegrityPolicy().assess(text)
        findings.append(_finding("ARC-11", education["allowed"], [] if education["allowed"] else ["academic integrity"], "STUDY_PLANNING"))
        engineering = EngineeringSafetyPolicy().assess(text)
        findings.append(_finding("ARC-13", engineering["allowed"], engineering["reasons"], engineering["mode"]))
        collaboration = CollaborationSafetyPolicy().assess(text)
        findings.append(_finding("ARC-14", collaboration["allowed"], collaboration["reasons"], collaboration["mode"]))
        evolution = EvolutionSafetyPolicy().assess(text)
        findings.append(_finding("ARC-15", evolution["allowed"], evolution["reasons"], evolution["mode"]))
        world = WorldModelSafetyPolicy().assess(text)
        findings.append(_finding("ARC-16", world["allowed"], world["reasons"], world["mode"]))
        science = ScientificSafetyPolicy().assess(text)
        findings.append(_finding("ARC-12", science["allowed"], science["reasons"], science["mode"]))
        neuro = assess_neuro_request(text)
        findings.append(_finding("ARC-05", neuro.allowed, [] if neuro.allowed else [neuro.reason], "COMPUTATIONAL"))
        findings.append(_finding("ARC-10", "hidden personal" not in text.casefold(), ["hidden personal"] if "hidden personal" in text.casefold() else [], "MEMORY_PERMISSION_REQUIRED"))
        return SafetyReport(allowed=all(item.allowed for item in findings), findings=findings, executed=False)
