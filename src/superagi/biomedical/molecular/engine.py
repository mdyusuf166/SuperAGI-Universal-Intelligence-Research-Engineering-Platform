from __future__ import annotations
from ..adapters import RDKitAdapter
from .validation import MoleculeValidator
from .descriptors import DescriptorEngine
from .fingerprints import FingerprintEngine
from .similarity import MolecularSimilarity


class MolecularEngine:
    def __init__(self, adapter=None) -> None:
        self.adapter = adapter or RDKitAdapter(); self.validator = MoleculeValidator(self.adapter); self.descriptor_engine = DescriptorEngine(self.adapter); self.fingerprint_engine = FingerprintEngine(self.adapter); self.similarity_engine = MolecularSimilarity(self.adapter)
    def validate(self, smiles): return self.validator.validate(smiles)
    def parse(self, smiles):
        validation = self.validate(smiles)
        return {"status": validation.adapter_status, "smiles": validation.normalized_value, "valid": validation.valid, "limitations": validation.errors}
    def descriptors(self, smiles): return self.descriptor_engine.calculate(smiles)
    def fingerprint(self, smiles): return self.fingerprint_engine.generate(smiles)
    def similarity(self, smiles_a, smiles_b): return self.similarity_engine.compare(smiles_a, smiles_b)
