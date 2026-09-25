"""Demo A: conceptual environmental monitor. CONCEPTUAL / SIMULATION-ONLY."""

from superagi.engineering import (
    EngineeringConstraint,
    EngineeringPipeline,
    EngineeringRequirement,
)


def build():
    requirement = EngineeringRequirement(statement="Measure environmental data with low power.", verification_method="simulation")
    constraint = EngineeringConstraint(kind="power", limit="low")
    result = EngineeringPipeline().run(
        "Design a conceptual low-power autonomous environmental monitoring system.",
        [requirement],
        [constraint],
    )
    design = result["design"]
    return {
        "classification": result["classification"],
        "status": result["status"],
        "requirements": [item.statement for item in design.requirements],
        "constraints": [{"kind": item.kind, "limit": item.limit} for item in design.constraints],
        "components": [item.name for item in design.components],
        "interfaces": [item.name for item in design.interfaces],
        "power": [item for item in design.decisions if item.startswith("Power consideration")],
        "control": result["control_proposal"].model_dump(),
        "simulation": {"status": result["simulation"].status, "backend": result["simulation"].backend, "limitations": result["simulation"].limitations},
        "verification": {"status": result["verification"].status, "checks": result["verification"].checks, "limitations": result["verification"].limitations},
        "tradeoffs": {"recommendation": result["tradeoff"].recommendation, "reason": result["tradeoff"].reason},
        "design_review": {"status": result["review"].status, "accepted": result["review"].accepted, "issues": result["review"].issues},
        "stages": result["stages"],
        "report": result["report"],
    }


def main():
    report = build()
    print("CONCEPTUAL / SIMULATION-ONLY")
    print(report["report"])
    for key in ("status", "requirements", "constraints", "components", "interfaces", "power", "control", "simulation", "verification", "tradeoffs", "design_review", "stages"):
        print(f"{key}: {report[key]}")
    return report


if __name__ == "__main__":
    main()
