"""Deterministic PID step. Actuator dispatch is refused through the ARC-07 policy."""

from __future__ import annotations

import math

from superagi.robotics.models import RobotCommand
from superagi.robotics.safety.policies import RoboticsSafetyPolicy

from .models import SIMULATION_CONTROL, ControlValidationResult, ControllerConfiguration, SimulationControlResult


def _is_finite(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


class ControlValidator:
    def validate(self, config: ControllerConfiguration, setpoint: float = 0.0, measured: float = 0.0) -> ControlValidationResult:
        issues: list[str] = []
        for name, gain in (("kp", config.kp), ("ki", config.ki), ("kd", config.kd)):
            if not _is_finite(gain):
                issues.append(f"invalid gains: {name}")
        if not _is_finite(config.output_min) or not _is_finite(config.output_max) or config.output_min > config.output_max:
            issues.append("invalid limits")
        if not _is_finite(config.dt) or config.dt <= 0 or not _is_finite(setpoint) or not _is_finite(measured):
            issues.append("invalid configuration")
        return ControlValidationResult(valid=not issues, issues=issues, classification=SIMULATION_CONTROL)


class SimulationController:
    def __init__(self, policy: RoboticsSafetyPolicy | None = None) -> None:
        self.policy = policy or RoboticsSafetyPolicy()

    def assess_actuator(self, request: str) -> dict:
        physical = any(token in request.casefold() for token in ("physical", "actuator", "deploy", "hardware"))
        command = RobotCommand(command_type="actuator" if physical else "simulation_control", parameters={"request": request}, requires_approval=physical)
        decision = self.policy.assess(command, approved=False)
        allowed = bool(decision.allowed) and not physical
        return {
            "allowed": allowed,
            "classification": SIMULATION_CONTROL,
            "robotics_mode": decision.mode,
            "reason": decision.reason,
            "command_sent": False,
        }

    def step(self, config: ControllerConfiguration, setpoint: float, measured: float, *, integral: float = 0.0, previous_error: float = 0.0) -> SimulationControlResult:
        gate = self.policy.assess(RobotCommand(command_type="simulation_control", parameters={"classification": SIMULATION_CONTROL}, requires_approval=False), approved=False)
        check = ControlValidator().validate(config, setpoint, measured)
        issues = list(check.issues)
        if not gate.allowed:
            issues.append(gate.reason)
        if issues:
            return SimulationControlResult(
                setpoint=float(setpoint) if _is_finite(setpoint) else 0.0,
                measured=float(measured) if _is_finite(measured) else 0.0,
                error=0.0,
                proportional=0.0,
                integral=0.0,
                derivative=0.0,
                integral_state=float(integral) if _is_finite(integral) else 0.0,
                output=0.0,
                bounded_output=0.0,
                saturated=False,
                valid=False,
                issues=issues,
                classification=SIMULATION_CONTROL,
                command_sent=False,
                robotics_mode=gate.mode,
            )
        error = float(setpoint) - float(measured)
        integral_state = float(integral) + error * float(config.dt)
        proportional = float(config.kp) * error
        integral_term = float(config.ki) * integral_state
        derivative = float(config.kd) * (error - float(previous_error)) / float(config.dt)
        output = proportional + integral_term + derivative
        bounded = min(max(output, float(config.output_min)), float(config.output_max))
        return SimulationControlResult(
            setpoint=float(setpoint),
            measured=float(measured),
            error=error,
            proportional=proportional,
            integral=integral_term,
            derivative=derivative,
            integral_state=integral_state,
            output=output,
            bounded_output=bounded,
            saturated=bounded != output,
            valid=True,
            issues=[],
            classification=SIMULATION_CONTROL,
            command_sent=False,
            robotics_mode=gate.mode,
        )
