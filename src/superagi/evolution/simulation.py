"""Deterministic mock simulation. This is not a physical-world model."""

from __future__ import annotations

from .models import (
    BackendStatus,
    ResultClassification,
    SimulationAction,
    SimulationObservation,
    SimulationResult,
    SimulationScenario,
    SimulationState,
    SimulationTransition,
    StateVariable,
)


def _apply(state: SimulationState, action: SimulationAction, step: int) -> SimulationState:
    values = [(item.name, item.value) for item in state.variables]
    index = {name: position for position, (name, _value) in enumerate(values)}
    for delta in action.deltas:
        if delta.name not in index:
            raise KeyError(delta.name)
        position = index[delta.name]
        name, current = values[position]
        values[position] = (name, current + delta.value)
    return SimulationState(step=step, variables=[StateVariable(name=name, value=value) for name, value in values])


def _terminal(state: SimulationState, scenario: SimulationScenario) -> bool:
    rule = scenario.termination
    if state.step >= rule.max_steps:
        return True
    if rule.variable is not None and rule.threshold is not None:
        try:
            return state.value(rule.variable) >= rule.threshold
        except KeyError:
            return False
    return False


class SimulationBackend:
    name = "backend"
    availability = BackendStatus.UNAVAILABLE

    def run(self, scenario: SimulationScenario) -> SimulationResult:
        raise NotImplementedError


class UnavailableSimulationBackend(SimulationBackend):
    name = "unavailable"
    availability = BackendStatus.UNAVAILABLE

    def run(self, scenario: SimulationScenario) -> SimulationResult:
        return SimulationResult(
            scenario_id=scenario.id,
            backend=self.name,
            status=BackendStatus.UNAVAILABLE,
            classification=ResultClassification.BACKEND_UNAVAILABLE,
            limitations=["No domain-fidelity simulator is configured. No mock trajectory was substituted."],
            provenance=scenario.provenance,
        )


class MockSimulationBackend(SimulationBackend):
    name = "deterministic-mock"
    availability = BackendStatus.MOCK

    def run(self, scenario: SimulationScenario) -> SimulationResult:
        state = scenario.initial_state.model_copy(deep=True)
        trace = [state]
        transitions: list[SimulationTransition] = []
        observations = [SimulationObservation(step=0, readings=list(state.variables))]
        for action in scenario.actions:
            if _terminal(state, scenario):
                break
            try:
                nxt = _apply(state, action, state.step + 1)
            except KeyError as exc:
                failed = state.model_copy(deep=True)
                failed.terminal = True
                return SimulationResult(
                    scenario_id=scenario.id,
                    backend=self.name,
                    status=BackendStatus.FAILED,
                    classification=ResultClassification.MOCK_SIMULATION,
                    step_count=len(trace) - 1,
                    trace=trace,
                    transitions=transitions,
                    observations=observations,
                    limitations=[f"Unknown state variable in action {action.name}: {exc.args[0]}. Mock simulation stopped."],
                    provenance=scenario.provenance,
                )
            transitions.append(SimulationTransition(step=nxt.step, action=action.name, before=list(state.variables), after=list(nxt.variables)))
            observations.append(SimulationObservation(step=nxt.step, readings=list(nxt.variables)))
            state = nxt
            trace.append(state)
            if _terminal(state, scenario):
                break
        state.terminal = True
        trace[-1] = state
        return SimulationResult(
            scenario_id=scenario.id,
            backend=self.name,
            status=BackendStatus.COMPLETED,
            classification=ResultClassification.MOCK_SIMULATION,
            step_count=len(transitions),
            trace=trace,
            transitions=transitions,
            observations=observations,
            limitations=["MOCK_SIMULATION. Deterministic arithmetic on declared variables. Not physical-world fidelity."],
            provenance=scenario.provenance,
        )
