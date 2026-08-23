from superagi.neuro.neurons import integrate_and_fire
from superagi.neuro.networks import NeuronNetwork, connect
from superagi.neuro.models import SimulationConfig
from superagi.neuro.simulation import NeuroSimulationEngine
from superagi.neuro.signals import SpikeTrainAnalyzer
a,b=integrate_and_fire(),integrate_and_fire(); result=NeuroSimulationEngine().run(NeuronNetwork(neurons=[a,b],connections=[connect(a.id,b.id,1)]),SimulationConfig(duration=10,timestep=.1)); analyzer=SpikeTrainAnalyzer()
print("SUPERAGI ARC-05 NEUROCOMPUTING DEMO\nBackend:",result.backend,"\nNeurons:",2,"\nConnections:",1,"\nSpike count:",sum(analyzer.spike_count(s) for s in result.spikes),"\nPopulation rate:",analyzer.population_rate(result.spikes),"\nSIMPLIFIED COMPUTATIONAL NEUROSCIENCE MODEL")
