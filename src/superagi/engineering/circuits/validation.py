"""Conceptual circuit checks. No SPICE or external simulator is required."""

from __future__ import annotations

import math

SUPPORTED_COMPONENT_TYPES = (
    "resistor",
    "capacitor",
    "inductor",
    "diode",
    "transistor",
    "logic_gate",
    "and",
    "or",
    "not",
    "nand",
    "nor",
    "xor",
    "xnor",
    "voltage_source",
    "current_source",
)

_NODE_LIMITS = {
    "resistor": (2, 2),
    "capacitor": (2, 2),
    "inductor": (2, 2),
    "diode": (2, 2),
    "transistor": (3, 3),
    "voltage_source": (2, 2),
    "current_source": (2, 2),
    "not": (2, 2),
    "logic_gate": (2, 8),
    "and": (3, 8),
    "or": (3, 8),
    "nand": (3, 8),
    "nor": (3, 8),
    "xor": (3, 8),
    "xnor": (3, 8),
}

_POSITIVE_KINDS = {"resistor", "capacitor", "inductor", "voltage_source", "current_source"}
_SOURCE_KINDS = {"voltage_source", "current_source"}


def expected_terminals(component) -> list[str]:
    if component.terminals:
        return list(component.terminals)
    kind = component.kind.casefold()
    if kind == "transistor":
        return ["base", "collector", "emitter"]
    if kind in {"and", "or", "nand", "nor", "xor", "xnor"}:
        return ["a", "b", "y"]
    if kind == "not":
        return ["a", "y"]
    if kind == "logic_gate":
        return [f"t{index}" for index in range(len(component.nodes))]
    return [str(index + 1) for index in range(len(component.nodes))]


def _finite_number(value):
    if isinstance(value, bool) or isinstance(value, str):
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                return None
        else:
            return None
    if isinstance(value, (int, float)) and math.isfinite(value):
        return float(value)
    return None


class CircuitValidator:
    def validate(self, circuit):
        issues: list[str] = []
        seen: set[str] = set()

        def add(code: str) -> None:
            if code not in seen:
                seen.add(code)
                issues.append(code)

        identifiers = [component.identifier for component in circuit.components]
        if len(identifiers) != len(set(identifiers)):
            add("duplicate component IDs")
        known = set(identifiers)
        connected_nodes: set[str] = set()

        for component in circuit.components:
            kind = component.kind.casefold()
            if kind not in SUPPORTED_COMPONENT_TYPES:
                add("unsupported component types")
                continue
            connected_nodes.update(component.nodes)
            if any(node not in circuit.nodes for node in component.nodes):
                add("invalid terminals")
            low, high = _NODE_LIMITS[kind]
            if not (low <= len(component.nodes) <= high) or len(set(component.nodes)) != len(component.nodes):
                add("invalid terminals")
            if kind in _SOURCE_KINDS and len(component.nodes) >= 2 and component.nodes[0] == component.nodes[1]:
                add("invalid source configuration")
            number = None if component.value is None else _finite_number(component.value)
            if component.value is not None and number is None:
                add("invalid source configuration" if kind in _SOURCE_KINDS else "invalid component values")
            elif kind in _POSITIVE_KINDS and number is not None and number <= 0:
                add("invalid source configuration" if kind in _SOURCE_KINDS else "invalid component values")
            elif kind in _SOURCE_KINDS and number is None:
                add("invalid source configuration")

        required = set(getattr(circuit, "required_nodes", ()) or ())
        if any(node not in circuit.nodes for node in required) or any(node not in connected_nodes for node in required):
            add("disconnected required nodes")

        for connection in getattr(circuit, "connections", []):
            if not isinstance(connection, dict) or not all(isinstance(connection.get(key), str) and connection.get(key) for key in ("component", "terminal", "node")):
                add("malformed connections")
                continue
            if connection["component"] not in known:
                add("invalid component references")
                continue
            if connection["node"] not in circuit.nodes:
                add("malformed connections")
                continue
            component = next(item for item in circuit.components if item.identifier == connection["component"])
            if connection["terminal"] not in expected_terminals(component):
                add("invalid terminals")

        return {"valid": not issues, "issues": issues}


class CircuitSimulator:
    """Explicit unavailable boundary. Tests may enable the deterministic mock."""

    def __init__(self, available: bool = False) -> None:
        self.available = available

    def simulate(self, circuit):
        if not self.available:
            return {
                "status": "SIMULATION_BACKEND_UNAVAILABLE",
                "backend": None,
                "output": {},
                "limitations": ["No SPICE or external circuit simulator is available."],
            }
        return {
            "status": "SIMULATION_RESULT",
            "backend": "mock",
            "output": {"components": len(circuit.components)},
            "limitations": ["Deterministic mock only; not electrical or physical validation."],
        }
