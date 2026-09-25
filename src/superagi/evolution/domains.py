"""Domain simulation descriptors. Real domain backends stay UNAVAILABLE."""

from __future__ import annotations

from .models import BackendStatus, DomainSimulationDescriptor, ResultClassification, SimulationResult, SimulationScenario
from .simulation import MockSimulationBackend, UnavailableSimulationBackend


def _unavailable(domain: str, arc: str, reason: str) -> DomainSimulationDescriptor:
    return DomainSimulationDescriptor(domain=domain, arc=arc, status=BackendStatus.UNAVAILABLE, classification=ResultClassification.BACKEND_UNAVAILABLE, limitations=[reason])


DEFAULT_DESCRIPTORS = (
    _unavailable("biology", "ARC-04", "No biomedical dynamics simulator is configured."),
    _unavailable("chemistry", "ARC-04", "No chemistry simulator is configured."),
    _unavailable("neuro", "ARC-05", "No spiking-network simulator is configured."),
    _unavailable("quantum", "ARC-06", "No quantum hardware or circuit simulator is configured."),
    _unavailable("robotics", "ARC-07", "No physical or Gazebo/Isaac robot simulator is configured. Grid planning remains a separate deterministic planner."),
    _unavailable("cybersecurity", "ARC-08", "No live network simulator is configured."),
    _unavailable("education", "ARC-11", "No student-performance simulator is configured."),
    _unavailable("science", "ARC-12", "No laboratory or scientific dynamics simulator is configured."),
    _unavailable("engineering", "ARC-13", "No SPICE or physical engineering simulator is configured."),
    _unavailable("collaboration", "ARC-14", "No organizational dynamics simulator is configured."),
    _unavailable("economics", "ARC-15", "No economic simulator is configured."),
    _unavailable("space", "ARC-15", "No orbital simulator is configured."),
    _unavailable("environment", "ARC-15", "No earth-system simulator is configured."),
    _unavailable("social", "ARC-15", "No social-system simulator is configured."),
    DomainSimulationDescriptor(domain="deterministic-mock", arc="ARC-15", status=BackendStatus.MOCK, classification=ResultClassification.MOCK_SIMULATION, limitations=["Explicit deterministic mock. Not a domain-fidelity model."]),
)


class DomainSimulationAdapter:
    def __init__(self, descriptor: DomainSimulationDescriptor) -> None:
        self.descriptor = descriptor

    def simulate(self, scenario: SimulationScenario) -> SimulationResult:
        if self.descriptor.status != BackendStatus.MOCK:
            return UnavailableSimulationBackend().run(scenario)
        return MockSimulationBackend().run(scenario)


class DomainSimulationRegistry:
    def __init__(self, descriptors: tuple[DomainSimulationDescriptor, ...] = DEFAULT_DESCRIPTORS) -> None:
        self._items = {item.domain: item for item in descriptors}

    def register(self, descriptor: DomainSimulationDescriptor) -> None:
        self._items[descriptor.domain] = descriptor

    def get(self, domain: str) -> DomainSimulationDescriptor:
        try:
            return self._items[domain]
        except KeyError as exc:
            raise KeyError(f"Unknown simulation domain: {domain}") from exc

    def adapter(self, domain: str) -> DomainSimulationAdapter:
        return DomainSimulationAdapter(self.get(domain))

    def domains(self) -> list[str]:
        return sorted(self._items)
