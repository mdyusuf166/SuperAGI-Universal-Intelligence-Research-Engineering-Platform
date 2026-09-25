# ARC-13 Engineering Creator AGI

## 1. Purpose

ARC-13 is a conceptual engineering design layer inside SuperAGI. It turns a stated problem into requirements, constraints, a system architecture, a design review, and an engineering report. The results are computational proposals. They are not manufactured hardware, certified designs, or permission to build or deploy a physical system.

## 2. Engineering Creator AGI concept

"Engineering Creator AGI" here means a deterministic assistant that can draft and check an engineering concept. It does not invent physical facts, run a laboratory, or close a control loop on real equipment. Every numerical result in this package comes from local code with explicit inputs. Confidence stays limited, and unresolved checks stay visible in the report.

## 3. Architecture

The pipeline order is:

Problem → Requirements → Constraints → System Architecture → Subsystems → Components → Interfaces → Design → Tradeoffs → Simulation Proposal → Verification → Design Review → Engineering Report

A failed requirements, constraint, or safety check stops the pipeline. Later stages are not reported as if they had passed. An unavailable simulation backend returns `SIMULATION_BACKEND_UNAVAILABLE` instead of a successful completion. Critical design-review findings set the run to `FAILED`.

## 4. Package structure

```text
src/superagi/engineering/
  models.py          typed design records
  services.py        requirements, design, simulation, verification, tradeoffs, safety, review
  pipeline/          stage runner
  circuits/          conceptual components, netlists, validation
  embedded/          proposal-only MCU and peripheral records
  control/           simulation-only control step
  agents/            seven BaseAgent implementations
  registration.py    ARC-01 and ARC-09 registration
examples/engineering/
  engineering_creator_demo.py
  conceptual_4bit_arithmetic.py
  autonomous_research_robot.py
```

## 5. Requirements

`RequirementsManager` stores typed `EngineeringRequirement` records. A requirement needs a statement and a verification method. The pipeline rejects an empty requirement list and any requirement that is missing either field.

## 6. Constraints

`EngineeringConstraint` records a kind and a limit, such as power / low. An empty kind or limit fails the constraint stage. The design review treats an empty limit, or a decision that contains `VIOLATES:<kind>`, as a violated constraint.

## 7. Systems Engineering

`DesignEngine.propose` builds a conceptual architecture with subsystems, components, and interfaces. `SystemsEngineeringAgent` runs that path through the shared pipeline. The architecture is a typed sketch, not a verified system model.

## 8. Circuit Design

`Circuit`, `CircuitComponent`, and `Netlist` describe a conceptual circuit. Supported kinds are resistor, capacitor, inductor, diode, transistor, logic gates (`logic_gate`, `and`, `or`, `not`, `nand`, `nor`, `xor`, `xnor`), voltage source, and current source. There is no SPICE netlist solver in this package.

## 9. Computer Engineering

`ComputerArchitecture` and `ArchitectureAgent` can record a conceptual CPU, memory, bus, and I/O description. This is a labeled block diagram in data form. It does not synthesize an ISA, boot firmware, or a board.

## 10. Embedded Engineering

`engineering.embedded` provides proposal-only MCU, GPIO, ADC, PWM, UART, SPI, I2C, and timer records. `EmbeddedValidator` reports duplicate pins, pin conflicts, invalid peripheral assignments, unsupported interfaces, invalid configurations, and resource conflicts. Every embedded result is marked `PROPOSAL_ONLY`. No pin is configured on a device.

## 11. Control Engineering

`engineering.control` computes a deterministic proportional, integral, and derivative step from a setpoint, a measured value, gains, and output limits. The result is marked `SIMULATION_CONTROL`. `command_sent` stays false. Requests that look like physical actuator commands are refused by the ARC-07 robotics safety policy.

## 12. Simulation

`EngineeringSimulationBackend` reports `UNAVAILABLE` when no backend is configured. `MockEngineeringSimulationBackend` returns a deterministic `SIMULATION_RESULT` for tests and demos, and its limitations say that the mock is not hardware validation. `CircuitSimulator` returns `SIMULATION_BACKEND_UNAVAILABLE` unless a test explicitly enables the same kind of mock.

## 13. Optimization

`EngineeringOptimizer.minimize` ranks candidate dictionaries by cost plus power, then by higher performance. It is a bounded local comparison of numbers the caller supplies. It is not a physical design search.

## 14. Tradeoff Analysis

`TradeoffAnalyzer.compare` sums the caller-supplied criterion scores and recommends the lowest total. The pipeline uses a fixed low-power versus high-performance example so the recommendation is reproducible. The reason string states that rule.

## 15. Verification

`EngineeringVerifier` checks that requirements, constraints, subsystems, compatible interfaces, and provenance are present. A passed check means the record is internally complete. The limitation on every verification result is that this is not physical certification.

## 16. Design Review

`DesignReview` is the review service. It reports:

- missing requirements
- violated constraints
- interface incompatibilities
- unsupported assumptions
- missing provenance
- unavailable simulation
- unresolved risks

Severities are `INFO`, `WARNING`, `ERROR`, and `CRITICAL`. Error and critical findings set `accepted` to false. Critical findings set the status to `REJECTED`. `DesignReviewAgent` returns `success=false` when a critical finding is present and copies the findings into the agent output.

## 17. Engineering Agents

These agents subclass or follow `BaseAgent` from ARC-01:

- `EngineeringAgent`
- `SystemsEngineeringAgent`
- `CircuitDesignAgent`
- `EmbeddedAgent`
- `ControlAgent`
- `ArchitectureAgent`
- `DesignReviewAgent`

They expose typed metadata and return `AgentResult`. They do not store a hidden chain of thought. `register_engineering_agents` adds them to an `AgentRegistry` and, when provided, to the ARC-09 `AgentCapabilityRegistry`.

## 18. Pipeline

`EngineeringPipeline.run(problem, requirements, constraints)` is the single runner. Optional arguments are a simulation backend and an ARC-02 `UniversalMemory`. Cancellation returns `CANCELLED` before any design work. The completed report is labeled `CONCEPTUAL / SIMULATION-ONLY`.

## 19. ARC-07 integration

Robot path examples call the existing `AStarPlanner`. Control and actuator checks call `RoboticsSafetyPolicy` and `RobotCommand`. Physical commands keep `requires_approval` true and are not approved, so the robotics policy stays in `SIMULATION_ONLY`. ARC-13 does not add a second robotics safety system and does not command a robot.

## 20. ARC-09 integration

Engineering descriptors use domain `engineering`, the agent's capability names, and safety level `low`. `AgentCapabilityRegistry.discover` can find them by capability, domain, and safety level. A request for a critical safety level or a physical-deployment domain does not return these agents. Science and robotics descriptors can be registered beside them by the caller; ARC-13 does not replace the orchestrator.

## 21. ARC-12 integration

The research-robot demo builds a `ScientificQuestion` and an `ExperimentDesigner` proposal. That proposal remains non-executing. ARC-13 does not run an experiment, call a laboratory, or treat a hypothesis as a result.

## 22. Memory/provenance

Designs carry a `provenance` list. The default entry is `engineering-pipeline`. If a `UniversalMemory` is passed to the pipeline, the problem text is stored through that existing memory service and the memory id is appended to the design provenance. ARC-13 does not create its own memory store.

## 23. Safety boundaries

`EngineeringSafetyPolicy` rejects requests that ask for real or physical hardware, firmware flashing, destructive operations, unsafe actuators, dangerous electrical operations, laboratory execution, or autonomous physical deployment. Conceptual design, simulation, verification, risk analysis, and test planning remain allowed. Rejection is a failed pipeline stage, not a silent edit of the request. Nothing in this package is a safety certification.

## 24. Examples

From the repository root, with `PYTHONPATH=src`:

```powershell
$env:PYTHONPATH = "src"
python examples/engineering/engineering_creator_demo.py
python examples/engineering/conceptual_4bit_arithmetic.py
python examples/engineering/autonomous_research_robot.py
```

Demo A is a low-power environmental monitor proposal. Demo B is a conceptual 4-bit adder and subtractor with a netlist and design review. Demo C is a simulated research rover that stops at a non-executing experiment proposal. Demo B prints `CONCEPTUAL CIRCUIT` and `NO PHYSICAL EXECUTION`. Demo C prints `SIMULATION ONLY` and `CONCEPTUAL RESEARCH SYSTEM`.

## 25. Limitations

This layer does not design a board that can be fabricated, validate electrical behavior, flash a microcontroller, stabilize a real plant, or approve field deployment. Mock simulation counts components or evaluates local arithmetic. It does not solve a circuit, a dynamic system, or a physical robot. Gate-level demo netlists are structural sketches; the 4-bit sums are computed by local integer logic, not by an electrical simulator. Tradeoffs only rank the numbers they are given. Agents do not learn across runs unless the caller stores something in ARC-02 memory.

## 26. Future extension points

A later arc can add an explicitly optional simulation adapter behind `EngineeringSimulationBackend` or `CircuitSimulator`. That adapter would still need to return an unavailable status when it is not configured. Physical I/O, laboratory execution, manufacturing release, and safety certification are outside ARC-13 and are not implied by these extension points.
