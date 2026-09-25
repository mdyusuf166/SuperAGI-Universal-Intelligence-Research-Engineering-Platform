"""Simulation-only control records. These values are never sent to an actuator."""

from __future__ import annotations

from pydantic import Field

from ..models import EM

SIMULATION_CONTROL = "SIMULATION_CONTROL"


class ControllerConfiguration(EM):
    kp: float
    ki: float
    kd: float
    output_min: float
    output_max: float
    dt: float = 1.0


class ControlValidationResult(EM):
    valid: bool
    issues: list[str] = Field(default_factory=list)
    classification: str = SIMULATION_CONTROL


class SimulationControlResult(EM):
    setpoint: float
    measured: float
    error: float
    proportional: float
    integral: float
    derivative: float
    integral_state: float
    output: float
    bounded_output: float
    saturated: bool = False
    valid: bool = True
    issues: list[str] = Field(default_factory=list)
    classification: str = SIMULATION_CONTROL
    command_sent: bool = False
    robotics_mode: str = "SIMULATION_ONLY"
