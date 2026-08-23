from superagi.quantum import CircuitEngine,QuantumExperiment,QuantumSimulationEngine
e=CircuitEngine(); c=e.add_gate(e.add_gate(e.create(2,2),"H",0),"CX",0,1); r=QuantumSimulationEngine().run(QuantumExperiment(circuit=c))
print("SUPERAGI ARC-06 QUANTUM DEMO\nBackend:",r.backend,"\nQubits:",c.num_qubits,"\nShots:",r.shots,"\nCounts:",r.counts,"\nProbabilities:",r.probabilities,"\nSimulation/HW: simulation\nLimitations:",r.limitations)
