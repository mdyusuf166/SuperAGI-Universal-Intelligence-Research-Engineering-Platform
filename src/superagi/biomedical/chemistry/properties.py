from __future__ import annotations
from ..molecular.descriptors import DescriptorEngine
class PropertyCalculator:
    def __init__(self, rdkit_adapter): self.engine = DescriptorEngine(rdkit_adapter)
    def calculate(self, molecule): return self.engine.calculate(molecule.smiles, molecule.id)
