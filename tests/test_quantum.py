from superagi.quantum import CircuitEngine,QuantumExperiment,QuantumSimulationEngine
def test_mock_quantum_simulation():
 e=CircuitEngine(); c=e.create(2,2); c=e.add_gate(c,"H",0); c=e.add_gate(c,"CX",0,1); r=QuantumSimulationEngine().run(QuantumExperiment(circuit=c)); assert r.status=="SIMULATION_RESULT" and r.is_simulation
def test_backend_unavailable():
 c=CircuitEngine().create(1); assert QuantumSimulationEngine().run(QuantumExperiment(circuit=c,backend="qiskit")).status=="UNAVAILABLE"
