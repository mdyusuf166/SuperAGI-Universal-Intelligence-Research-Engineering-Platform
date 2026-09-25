"""Demo B: conceptual 4-bit arithmetic. CONCEPTUAL CIRCUIT. NO PHYSICAL EXECUTION."""

from superagi.engineering import DesignEngine, DesignReview, EngineeringConstraint, EngineeringRequirement
from superagi.engineering.circuits import Circuit, CircuitComponent, CircuitValidator, Netlist


def full_adder(a, b, carry_in):
    total = (a & 1) + (b & 1) + (carry_in & 1)
    return {"sum": total & 1, "carry": total >> 1}


def add4(a, b):
    if not (0 <= a <= 15 and 0 <= b <= 15):
        raise ValueError("4-bit operands must be in 0..15")
    carry = 0
    bits = []
    for index in range(4):
        step = full_adder((a >> index) & 1, (b >> index) & 1, carry)
        bits.append(step["sum"])
        carry = step["carry"]
    return {"sum": sum(bit << index for index, bit in enumerate(bits)), "carry": carry}


def sub4(a, b):
    if not (0 <= a <= 15 and 0 <= b <= 15):
        raise ValueError("4-bit operands must be in 0..15")
    inverted = (~b) & 0xF
    carry = 1
    bits = []
    for index in range(4):
        step = full_adder((a >> index) & 1, (inverted >> index) & 1, carry)
        bits.append(step["sum"])
        carry = step["carry"]
    return {"difference": sum(bit << index for index, bit in enumerate(bits)), "borrow": int(carry == 0)}


def conceptual_circuit():
    nodes = [f"A{i}" for i in range(4)] + [f"B{i}" for i in range(4)] + [f"S{i}" for i in range(4)] + [f"C{i}" for i in range(5)] + ["SUB", "BORROW"]
    circuit = Circuit(nodes, required_nodes=["A0", "S0", "C4", "BORROW"])
    circuit.add(CircuitComponent(identifier="FA0", kind="logic_gate", nodes=["A0", "B0", "C0", "S0", "C1"], terminals=["a", "b", "cin", "sum", "cout"]))
    circuit.add(CircuitComponent(identifier="FA1", kind="logic_gate", nodes=["A1", "B1", "C1", "S1", "C2"], terminals=["a", "b", "cin", "sum", "cout"]))
    circuit.add(CircuitComponent(identifier="FA2", kind="logic_gate", nodes=["A2", "B2", "C2", "S2", "C3"], terminals=["a", "b", "cin", "sum", "cout"]))
    circuit.add(CircuitComponent(identifier="FA3", kind="logic_gate", nodes=["A3", "B3", "C3", "S3", "C4"], terminals=["a", "b", "cin", "sum", "cout"]))
    circuit.add(CircuitComponent(identifier="INV", kind="xor", nodes=["SUB", "B0", "BORROW"], terminals=["a", "b", "y"]))
    for identifier, pairs in {
        "FA0": (("a", "A0"), ("b", "B0"), ("cin", "C0"), ("sum", "S0"), ("cout", "C1")),
        "FA1": (("a", "A1"), ("b", "B1"), ("cin", "C1"), ("sum", "S1"), ("cout", "C2")),
        "FA2": (("a", "A2"), ("b", "B2"), ("cin", "C2"), ("sum", "S2"), ("cout", "C3")),
        "FA3": (("a", "A3"), ("b", "B3"), ("cin", "C3"), ("sum", "S3"), ("cout", "C4")),
        "INV": (("a", "SUB"), ("b", "B0"), ("y", "BORROW")),
    }.items():
        for terminal, node in pairs:
            circuit.connect(identifier, terminal, node)
    return circuit


def build():
    circuit = conceptual_circuit()
    validation = CircuitValidator().validate(circuit)
    design = DesignEngine().propose(
        "Conceptual 4-bit adder and subtractor.",
        [EngineeringRequirement(statement="Compute 4-bit addition and subtraction.", verification_method="review", measurable=True)],
        [EngineeringConstraint(kind="execution", limit="conceptual")],
    )
    review = DesignReview().review(design)
    return {
        "classification": ["CONCEPTUAL CIRCUIT", "NO PHYSICAL EXECUTION"],
        "inputs": ["A0-A3", "B0-B3", "SUB"],
        "outputs": ["S0-S3", "C4", "BORROW"],
        "logic_blocks": [component.identifier for component in circuit.components],
        "addition": add4(9, 3),
        "addition_overflow": add4(15, 1),
        "subtraction": sub4(5, 3),
        "subtraction_borrow": sub4(3, 5),
        "carry": add4(15, 1)["carry"],
        "borrow": sub4(3, 5)["borrow"],
        "netlist": Netlist(circuit).entries,
        "validation": validation,
        "design_review": {"status": review.status, "accepted": review.accepted},
    }


def main():
    report = build()
    print("CONCEPTUAL CIRCUIT")
    print("NO PHYSICAL EXECUTION")
    for key, value in report.items():
        print(f"{key}: {value}")
    return report


if __name__ == "__main__":
    main()
