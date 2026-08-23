from __future__ import annotations
from ..models import Neuron
def integrate_and_fire(**parameters):
    defaults={"threshold":1.0,"reset":0.0,"membrane_potential":0.0,"resting_potential":0.0,"time_constant":10.0,"refractory_period":2.0}
    defaults.update(parameters); return Neuron(parameters=defaults, metadata={"classification":"SIMPLIFIED COMPUTATIONAL MODEL"})
