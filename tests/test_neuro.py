from superagi.neuro.neurons import integrate_and_fire
from superagi.neuro.networks import NeuronNetwork, connect
from superagi.neuro.simulation import NeuroSimulationEngine
from superagi.neuro.models import SimulationConfig
from superagi.neuro.signals import SpikeTrainAnalyzer
def test_mock_neuro_simulation():
    a,b=integrate_and_fire(),integrate_and_fire(); network=NeuronNetwork(neurons=[a,b],connections=[connect(a.id,b.id,1.0)])
    result=NeuroSimulationEngine().run(network,SimulationConfig(duration=10,timestep=.1)); assert result.status=="SIMULATION_RESULT"; assert SpikeTrainAnalyzer().spike_count(result.spikes[0])==1
def test_unavailable_backend(): assert NeuroSimulationEngine().run(NeuronNetwork(),SimulationConfig(duration=1,timestep=.1,backend="brian2")).status=="UNAVAILABLE"
