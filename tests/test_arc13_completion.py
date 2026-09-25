import asyncio
import importlib.util
from pathlib import Path

import pytest

from superagi.core.agents import AgentRegistry
from superagi.core.models import AgentContext, Task
from superagi.engineering import (
    STAGE_ORDER,
    DesignEngine,
    DesignReview,
    EngineeringConstraint,
    EngineeringOptimizer,
    EngineeringPipeline,
    EngineeringRequirement,
    EngineeringSafetyPolicy,
    EngineeringSimulationBackend,
    EngineeringVerifier,
    MockEngineeringSimulationBackend,
    ReviewSeverity,
    TradeoffAnalyzer,
    register_engineering_agents,
)
from superagi.engineering.agents import (
    ArchitectureAgent,
    CircuitDesignAgent,
    ControlAgent,
    DesignReviewAgent,
    EmbeddedAgent,
    EngineeringAgent,
    SystemsEngineeringAgent,
)
from superagi.engineering.circuits import Circuit, CircuitComponent, CircuitSimulator, CircuitValidator
from superagi.engineering.control import ControllerConfiguration, SimulationController
from superagi.engineering.embedded import ADC, GPIO, MCU, PWM, SPI, UART, EmbeddedDesign, EmbeddedValidator, I2C, Timer
from superagi.engineering.pipeline import EngineeringPipeline as PipelineFacade
from superagi.memory import UniversalMemory
from superagi.orchestration import AgentCapabilityRegistry
from superagi.robotics.models import RobotCommand
from superagi.robotics.planning.path_planner import AStarPlanner
from superagi.robotics.safety.policies import RoboticsSafetyPolicy
from superagi.science.experiment import ExperimentDesigner
from superagi.science.integration import science_agent_descriptor
from superagi.science.models import ScientificQuestion

ROOT = Path(__file__).resolve().parents[1]
AGENTS = (EngineeringAgent, SystemsEngineeringAgent, CircuitDesignAgent, EmbeddedAgent, ControlAgent, ArchitectureAgent, DesignReviewAgent)


def load_demo(filename):
    path = ROOT / "examples" / "engineering" / filename
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def requirement(statement="measure the signal", method="review"):
    return EngineeringRequirement(statement=statement, verification_method=method)


def constraint(kind="power", limit="low"):
    return EngineeringConstraint(kind=kind, limit=limit)


def context(task, **values):
    return AgentContext(task_id=task.id, values=values)


def run_agent(agent, **values):
    task = Task(description=agent.metadata.name)
    return asyncio.run(agent.run(task, context(task, **values)))


def test_requirements_constraints_architecture_and_optimizer():
    manager_requirement = requirement()
    design = DesignEngine().propose("conceptual monitor", [manager_requirement], [constraint()])
    assert design.requirements[0].statement == "measure the signal"
    assert design.constraints[0].limit == "low"
    assert design.architecture.subsystems
    assert design.components
    assert design.interfaces
    assert EngineeringVerifier().verify(design).status == "VERIFIED"
    assert MockEngineeringSimulationBackend().simulate(design).status == "SIMULATION_RESULT"
    best = EngineeringOptimizer().minimize([{"cost": 3, "power": 3, "performance": 1}, {"cost": 1, "power": 1, "performance": 2}])
    tradeoff = TradeoffAnalyzer().compare({"low_power": {"cost": 1}, "high_performance": {"cost": 3}})
    assert best["cost"] == 1
    assert tradeoff.recommendation == "low_power"


def test_pipeline_completes_every_stage_and_records_provenance():
    memory = UniversalMemory()
    result = EngineeringPipeline(memory=memory).run("conceptual monitoring system", [requirement()], [constraint()])
    assert result["status"] == "COMPLETED"
    assert result["stages"] == list(STAGE_ORDER)
    assert result["classification"] == "CONCEPTUAL / SIMULATION-ONLY"
    assert result["control_proposal"].classification == "SIMULATION_CONTROL"
    assert result["control_proposal"].command_sent is False
    assert any(item.startswith("memory:") for item in result["design"].provenance)
    assert memory.provenance.records
    assert PipelineFacade is EngineeringPipeline


def test_pipeline_stops_on_failed_requirements_constraints_and_safety():
    requirements = EngineeringPipeline().run("conceptual", [EngineeringRequirement(statement="", verification_method="")])
    assert requirements["status"] == "FAILED"
    assert requirements["stages"] == ["problem", "requirements"]
    constraints = EngineeringPipeline().run("conceptual", [requirement()], [EngineeringConstraint(kind="power", limit="")])
    assert constraints["status"] == "FAILED"
    assert constraints["stages"] == ["problem", "requirements", "constraints"]
    safety = EngineeringPipeline().run("firmware flash the board", [requirement()], [constraint()])
    assert safety["status"] == "FAILED"
    assert safety["reason"] == "Safety policy rejected request."
    assert "engineering_report" not in safety["stages"]


def test_unavailable_simulation_is_explicit():
    result = EngineeringPipeline(backend=EngineeringSimulationBackend()).run("conceptual monitor", [requirement()], [constraint()])
    assert result["status"] == "SIMULATION_BACKEND_UNAVAILABLE"
    assert any(finding.category == "unavailable_simulation" for finding in result["review"].findings)


@pytest.mark.parametrize("text", ["physical hardware command", "destructive operation", "unsafe actuator command", "dangerous electrical operation", "unsafe laboratory execution", "autonomous physical deployment"])
def test_safety_rejects_physical_and_destructive_requests(text):
    assert EngineeringSafetyPolicy().assess(text)["allowed"] is False


@pytest.mark.parametrize("text", ["conceptual design", "simulation", "verification", "risk analysis", "test planning"])
def test_safety_keeps_design_alternatives_available(text):
    assert EngineeringSafetyPolicy().assess(text)["allowed"] is True


def test_circuit_validation_accepts_supported_parts_and_reports_each_fault():
    circuit = Circuit(["a", "b"])
    circuit.add(CircuitComponent(identifier="R1", kind="resistor", nodes=["a", "b"], value=1000))
    circuit.add(CircuitComponent(identifier="C1", kind="capacitor", nodes=["a", "b"], value=1e-6))
    circuit.add(CircuitComponent(identifier="L1", kind="inductor", nodes=["a", "b"], value=1e-3))
    circuit.add(CircuitComponent(identifier="D1", kind="diode", nodes=["a", "b"]))
    circuit.add(CircuitComponent(identifier="Q1", kind="transistor", nodes=["a", "b", "a"]))
    assert "invalid terminals" in CircuitValidator().validate(circuit)["issues"]

    valid = Circuit(["a", "b", "c"])
    valid.add(CircuitComponent(identifier="Q1", kind="transistor", nodes=["a", "b", "c"]))
    valid.add(CircuitComponent(identifier="V1", kind="voltage_source", nodes=["a", "b"], value=5))
    valid.add(CircuitComponent(identifier="I1", kind="current_source", nodes=["b", "c"], value=0.01))
    valid.add(CircuitComponent(identifier="G1", kind="and", nodes=["a", "b", "c"], terminals=["a", "b", "y"]))
    assert CircuitValidator().validate(valid)["valid"] is True

    duplicated = Circuit(["a", "b"])
    duplicated.add(CircuitComponent(identifier="R1", kind="resistor", nodes=["a", "b"]))
    duplicated.add(CircuitComponent(identifier="R1", kind="resistor", nodes=["a", "b"]))
    assert "duplicate component IDs" in CircuitValidator().validate(duplicated)["issues"]

    bad_value = Circuit(["a", "b"])
    bad_value.add(CircuitComponent(identifier="R1", kind="resistor", nodes=["a", "b"], value=-5))
    assert "invalid component values" in CircuitValidator().validate(bad_value)["issues"]

    bad_source = Circuit(["a", "b"])
    bad_source.add(CircuitComponent(identifier="V1", kind="voltage_source", nodes=["a", "b"]))
    assert "invalid source configuration" in CircuitValidator().validate(bad_source)["issues"]

    unsupported = Circuit(["a", "b"])
    unsupported.add(CircuitComponent(identifier="X1", kind="relay", nodes=["a", "b"]))
    assert "unsupported component types" in CircuitValidator().validate(unsupported)["issues"]

    disconnected = Circuit(["a", "b", "c"], required_nodes=["c"])
    disconnected.add(CircuitComponent(identifier="R1", kind="resistor", nodes=["a", "b"]))
    assert "disconnected required nodes" in CircuitValidator().validate(disconnected)["issues"]

    malformed = Circuit(["a", "b"])
    malformed.add(CircuitComponent(identifier="R1", kind="resistor", nodes=["a", "b"]))
    malformed.connections.append("bad")
    malformed.connect("missing", "1", "a")
    malformed.connect("R1", "gate", "a")
    issues = CircuitValidator().validate(malformed)["issues"]
    assert "malformed connections" in issues
    assert "invalid component references" in issues
    assert "invalid terminals" in issues
    assert CircuitSimulator().simulate(malformed)["status"] == "SIMULATION_BACKEND_UNAVAILABLE"
    assert CircuitSimulator(available=True).simulate(malformed)["status"] == "SIMULATION_RESULT"


def test_embedded_validation_and_conflicts():
    mcu = MCU(name="conceptual-mcu", pins=["P0", "P1", "P2", "P3", "P4", "P5"])
    design = EmbeddedDesign(mcu=mcu, gpio=[GPIO(pin="P0", direction="input")], adc=[ADC(pin="P1")], pwm=[PWM(pin="P2", frequency_hz=1000, duty_cycle=0.5)], uart=[UART(tx_pin="P3", rx_pin="P4")], timers=[Timer(name="tick", pin="P5", period_ms=10)])
    result = EmbeddedValidator().validate(design)
    assert result.valid is True
    assert result.mode == "PROPOSAL_ONLY"
    assert design.mode == "PROPOSAL_ONLY"

    duplicate = EmbeddedDesign(mcu=mcu, gpio=[GPIO(pin="P0", direction="input"), GPIO(pin="P0", direction="output")])
    conflict = EmbeddedDesign(mcu=mcu, gpio=[GPIO(pin="P0", direction="input")], adc=[ADC(pin="P0")])
    missing = EmbeddedDesign(mcu=mcu, gpio=[GPIO(pin="P99", direction="input")])
    unsupported = EmbeddedDesign(mcu=MCU(name="tiny", pins=["P0", "P1", "P2", "P3"], supported_interfaces=["GPIO"]), spi=[SPI(sclk="P0", mosi="P1", miso="P2", cs="P3")])
    invalid = EmbeddedDesign(mcu=mcu, pwm=[PWM(pin="P2", frequency_hz=1000, duty_cycle=2)])
    resources = EmbeddedDesign(mcu=MCU(name="one-uart", pins=["P0", "P1", "P2", "P3"], resources={"UART": 1, "GPIO": 8, "ADC": 8, "PWM": 8, "SPI": 1, "I2C": 2, "TIMER": 4}), uart=[UART(tx_pin="P0", rx_pin="P1"), UART(tx_pin="P2", rx_pin="P3")], i2c=[I2C(sda="P0", scl="P1", address=0x48), I2C(sda="P2", scl="P3", address=0x48)])
    assert "duplicate pins" in EmbeddedValidator().validate(duplicate).issues
    assert "pin conflicts" in EmbeddedValidator().validate(conflict).issues
    assert "invalid peripheral assignments" in EmbeddedValidator().validate(missing).issues
    assert "unsupported interfaces" in EmbeddedValidator().validate(unsupported).issues
    assert "invalid configurations" in EmbeddedValidator().validate(invalid).issues
    assert "resource conflicts" in EmbeddedValidator().validate(resources).issues


def test_control_terms_bounds_and_arc07_rejection():
    controller = SimulationController()
    result = controller.step(ControllerConfiguration(kp=2, ki=3, kd=4, output_min=-100, output_max=100), 10, 6, integral=1, previous_error=1)
    assert result.classification == "SIMULATION_CONTROL"
    assert result.command_sent is False
    assert result.error == 4
    assert result.proportional == 8
    assert result.integral == 15
    assert result.derivative == 12
    assert result.bounded_output == 35
    bounded = controller.step(ControllerConfiguration(kp=10, ki=0, kd=0, output_min=-1, output_max=1), 5, 0)
    assert bounded.valid is True
    assert bounded.saturated is True
    assert bounded.bounded_output == 1
    invalid = controller.step(ControllerConfiguration(kp=float("nan"), ki=0, kd=0, output_min=5, output_max=1, dt=0), 0, 0)
    assert invalid.valid is False
    assert any(item.startswith("invalid gains") for item in invalid.issues)
    assert "invalid limits" in invalid.issues
    assert "invalid configuration" in invalid.issues
    actuator = controller.assess_actuator("unsafe actuator command")
    assert actuator["allowed"] is False
    assert actuator["command_sent"] is False
    assert actuator["classification"] == "SIMULATION_CONTROL"
    assert RoboticsSafetyPolicy().assess(RobotCommand(command_type="move", requires_approval=True), approved=False).allowed is False


def test_design_review_categories_and_agent():
    design = DesignEngine().propose("conceptual monitor", [requirement(method="review")], [constraint()])
    clean = DesignReview().review(design)
    assert clean.status == "VERIFIED"
    assert clean.accepted is True
    design.requirements[0].measurable = False
    design.decisions.append("VIOLATES:power")
    design.interfaces[0].compatible = False
    design.assumptions.append("UNSUPPORTED: unlimited energy")
    design.provenance.clear()
    reviewed = DesignReview().review(design, simulation=EngineeringSimulationBackend().simulate(design), risks=["critical power hazard", "sensor drift"])
    categories = {finding.category for finding in reviewed.findings}
    assert categories >= {"missing_requirements", "violated_constraints", "interface_incompatibilities", "unsupported_assumptions", "missing_provenance", "unavailable_simulation", "unresolved_risks"}
    assert reviewed.accepted is False
    assert reviewed.status == "REJECTED"
    assert any(finding.severity == ReviewSeverity.CRITICAL for finding in reviewed.findings)
    rejected = DesignEngine().propose("autonomous physical deployment", [requirement()], [constraint()])
    agent_result = run_agent(DesignReviewAgent(), design=rejected)
    assert agent_result.success is False
    assert agent_result.output["critical"]
    accepted = run_agent(DesignReviewAgent(), design=DesignEngine().propose("conceptual monitor", [requirement()], [constraint()]))
    assert accepted.success is True


def test_every_engineering_agent_registers_and_is_discoverable():
    registry = AgentRegistry()
    capabilities = AgentCapabilityRegistry()
    created = register_engineering_agents(registry, capabilities)
    assert [type(agent) for agent in created] == list(AGENTS)
    assert len(capabilities.discover(["engineering"], domain="engineering", safety_level="low")) == 7
    assert capabilities.discover(["design_review"], domain="engineering", safety_level="low")[0].name == "design_review_agent"
    assert capabilities.discover(["engineering"], domain="engineering", safety_level="critical") == []
    assert capabilities.discover(["engineering"], domain="physical_deployment") == []
    payload = {"problem": "conceptual monitor", "requirements": [requirement()], "constraints": [constraint()]}
    for agent in created:
        if isinstance(agent, DesignReviewAgent):
            continue
        result = run_agent(agent, **payload)
        assert result.success is True
        assert result.output["agent"] == agent.metadata.name
    circuit = Circuit(["a", "b"])
    circuit.add(CircuitComponent(identifier="R1", kind="resistor", nodes=["a", "b"]))
    assert run_agent(CircuitDesignAgent(), circuit=circuit).output["simulation"]["status"] == "SIMULATION_BACKEND_UNAVAILABLE"
    embedded = EmbeddedDesign(mcu=MCU(name="mcu", pins=["P0"]), gpio=[GPIO(pin="P0", direction="input")])
    assert run_agent(EmbeddedAgent(), embedded=embedded).output["mode"] == "PROPOSAL_ONLY"
    control = run_agent(ControlAgent(), controller=ControllerConfiguration(kp=1, ki=0, kd=0, output_min=-1, output_max=1), setpoint=1, measured=0)
    assert control.output["classification"] == "SIMULATION_CONTROL"
    architecture = run_agent(ArchitectureAgent(), computer={"cpu": "conceptual", "memory": "conceptual", "bus": "conceptual"})
    assert architecture.output["classification"] == "CONCEPTUAL"


def test_arc07_arc09_and_arc12_boundaries():
    path = AStarPlanner().plan((0, 0), (2, 0))
    assert (path[0].x, path[0].y) == (0, 0)
    assert RoboticsSafetyPolicy().assess(RobotCommand(command_type="actuator", requires_approval=True), approved=False).mode == "SIMULATION_ONLY"
    registry = AgentCapabilityRegistry()
    register_engineering_agents(AgentRegistry(), registry)
    registry.register(science_agent_descriptor())
    assert registry.discover(["science"], domain="science")
    proposal = ExperimentDesigner().design(ScientificQuestion(question="How does a simulated sensor reading change?", variables=["reading"]))
    assert "NON-EXECUTING" in proposal.reproducibility


def test_public_facades_import():
    import superagi.engineering as engineering
    import superagi.engineering.agents as agents
    import superagi.engineering.circuits as circuits
    import superagi.engineering.control as control
    import superagi.engineering.embedded as embedded
    import superagi.engineering.pipeline as pipeline
    assert engineering.EngineeringPipeline is pipeline.EngineeringPipeline
    assert agents.DesignReviewAgent is DesignReviewAgent
    assert circuits.CircuitValidator is CircuitValidator
    assert control.SimulationController is SimulationController
    assert embedded.EmbeddedValidator is EmbeddedValidator
    assert engineering.register_engineering_agents is register_engineering_agents


def test_demo_b_arithmetic_and_demo_c_pipeline():
    demo_b = load_demo("conceptual_4bit_arithmetic.py")
    report = demo_b.build()
    assert report["classification"] == ["CONCEPTUAL CIRCUIT", "NO PHYSICAL EXECUTION"]
    assert report["addition"] == {"sum": 12, "carry": 0}
    assert report["addition_overflow"] == {"sum": 0, "carry": 1}
    assert report["subtraction"] == {"difference": 2, "borrow": 0}
    assert report["subtraction_borrow"] == {"difference": 14, "borrow": 1}
    assert report["validation"]["valid"] is True
    assert report["design_review"]["accepted"] is True
    assert demo_b.build()["netlist"] == report["netlist"]

    demo_c = load_demo("autonomous_research_robot.py")
    robot = demo_c.build()
    assert robot["classification"] == ["SIMULATION ONLY", "CONCEPTUAL RESEARCH SYSTEM"]
    assert robot["flow"] == demo_c.FLOW
    assert robot["pipeline_status"] == "COMPLETED"
    assert robot["navigation"][0] == {"x": 0, "y": 0}
    assert robot["navigation"][-1] == {"x": 3, "y": 1}
    assert robot["simulation"]["is_simulation"] is True
    assert robot["safety"]["physical_command_allowed"] is False
    assert robot["safety"]["command_sent"] is False
    assert robot["orchestration"] == {"engineering": 7, "science": 1, "robotics": 1}
    assert "NON-EXECUTING" in robot["experiment_proposal"]["reproducibility"]
    again = demo_c.build()
    assert again["navigation"] == robot["navigation"]
    assert again["engineering_report"] == robot["engineering_report"]


def test_demo_a_environmental_monitor():
    demo = load_demo("engineering_creator_demo.py")
    report = demo.build()
    assert report["classification"] == "CONCEPTUAL / SIMULATION-ONLY"
    assert report["status"] == "COMPLETED"
    assert report["requirements"]
    assert report["constraints"][0]["kind"] == "power"
    assert report["components"]
    assert report["interfaces"]
    assert report["power"]
    assert report["control"]["classification"] == "SIMULATION_CONTROL"
    assert report["simulation"]["status"] == "SIMULATION_RESULT"
    assert report["verification"]["status"] == "VERIFIED"
    assert report["tradeoffs"]["recommendation"] == "low_power"
    assert report["design_review"]["accepted"] is True
    assert report["stages"] == list(STAGE_ORDER)
    assert demo.build()["report"] == report["report"]
