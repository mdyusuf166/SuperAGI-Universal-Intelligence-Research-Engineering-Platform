from ..services import DesignEngine, DesignReview, EngineeringSafetyPolicy, EngineeringVerifier, MockEngineeringSimulationBackend, TradeoffAnalyzer
from ..control import ControllerConfiguration, SimulationController

STAGE_ORDER = [
    "problem",
    "requirements",
    "constraints",
    "system_architecture",
    "subsystems",
    "components",
    "interfaces",
    "design",
    "tradeoffs",
    "simulation_proposal",
    "verification",
    "design_review",
    "engineering_report",
]

_REPORT = "CONCEPTUAL / SIMULATION-ONLY engineering proposal; not autonomous engineering, physical validation, safety certification, manufacturing readiness, or deployment."


class EngineeringPipeline:
    def __init__(self, backend=None, memory=None):
        self.backend = backend or MockEngineeringSimulationBackend()
        self.memory = memory
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def _fail(self, stage, reason, safety=None):
        index = STAGE_ORDER.index(stage)
        return {"status": "FAILED", "stage": stage, "reason": reason, "stages": STAGE_ORDER[: index + 1], "safety": safety, "classification": "CONCEPTUAL / SIMULATION-ONLY"}

    def run(self, problem, requirements, constraints=()):
        if self.cancelled:
            return {"status": "CANCELLED", "stages": []}
        safety = EngineeringSafetyPolicy().assess(problem)
        if not safety["allowed"]:
            return self._fail("problem", "Safety policy rejected request.", safety)
        if not requirements or any(not getattr(item, "statement", "") or not getattr(item, "verification_method", "") for item in requirements):
            return self._fail("requirements", "Requirements validation failed.", safety)
        if any(not getattr(item, "kind", "") or not getattr(item, "limit", "") for item in constraints):
            return self._fail("constraints", "Constraint validation failed.", safety)
        design = DesignEngine().propose(problem, requirements, constraints)
        if self.memory is not None:
            record = self.memory.remember(problem, source="engineering", source_id=str(design.id), tags=("engineering", "arc13"))
            design.provenance.append(f"memory:{record.id}")
        if not design.architecture or not design.architecture.subsystems:
            return self._fail("system_architecture", "System architecture validation failed.", safety)
        control = SimulationController().step(ControllerConfiguration(kp=1.0, ki=0.0, kd=0.0, output_min=-1.0, output_max=1.0), setpoint=1.0, measured=0.0)
        if not control.valid or control.classification != "SIMULATION_CONTROL" or control.command_sent:
            failed = self._fail("design", "Control proposal failed validation.", safety)
            failed["control_proposal"] = control
            return failed
        tradeoff = TradeoffAnalyzer().compare({"low_power": {"power": 1.0, "cost": 2.0, "complexity": 2.0}, "high_performance": {"power": 5.0, "cost": 4.0, "complexity": 3.0}})
        simulation = self.backend.simulate(design)
        verification = EngineeringVerifier().verify(design)
        review = DesignReview().review(design, simulation=simulation)
        report = _REPORT
        status = "COMPLETED"
        reason = ""
        if not review.accepted:
            status = "FAILED"
            reason = "Design review rejected critical or error findings."
        elif getattr(simulation, "status", "") in {"UNAVAILABLE", "SIMULATION_BACKEND_UNAVAILABLE"}:
            status = "SIMULATION_BACKEND_UNAVAILABLE"
            reason = "Simulation backend unavailable."
            report = "SIMULATION_BACKEND_UNAVAILABLE. " + report
        elif verification.status != "VERIFIED" or review.status != "VERIFIED":
            status = "PARTIALLY_VERIFIED"
            reason = "Verification or design review is incomplete."
        return {
            "status": status,
            "stage": None if status == "COMPLETED" else "design_review",
            "reason": reason,
            "design": design,
            "simulation": simulation,
            "verification": verification,
            "review": review,
            "tradeoff": tradeoff,
            "control_proposal": control,
            "report": report,
            "stages": list(STAGE_ORDER),
            "safety": safety,
            "classification": "CONCEPTUAL / SIMULATION-ONLY",
        }
