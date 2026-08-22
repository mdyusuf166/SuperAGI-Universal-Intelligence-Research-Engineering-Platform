from __future__ import annotations
from ..adapters import DeepChemAdapter, ChempropAdapter, RDKitAdapter
from .properties import PropertyCalculator
from .prediction import PredictionResult
from .uncertainty import PredictionUncertainty

class ChemistryEngine:
    def __init__(self, *, deepchem_adapter=None, chemprop_adapter=None, rdkit_adapter=None) -> None:
        self.deepchem = deepchem_adapter or DeepChemAdapter(); self.chemprop = chemprop_adapter or ChempropAdapter(); self.rdkit = rdkit_adapter or RDKitAdapter(); self.properties = PropertyCalculator(self.rdkit)
    def calculate_properties(self, molecule): return self.properties.calculate(molecule)
    def predict_property(self, molecule, property_name, backend="deepchem") -> PredictionResult:
        adapter = self.deepchem if backend.lower() == "deepchem" else self.chemprop
        method = adapter.predict_property if backend.lower() == "deepchem" else adapter.molecular_property_prediction
        if not adapter.available and adapter.__class__.__name__ not in {"MockDeepChemAdapter", "MockChempropAdapter"}:
            return PredictionResult(molecule_id=molecule.id, property=property_name, model=adapter.__class__.__name__, backend=backend, status="UNAVAILABLE", source=adapter.__class__.__name__, limitations=[f"{backend} is unavailable; no prediction was made."])
        try:
            raw = method(molecule, property_name); value = raw.output.get("value")
            uncertainty = PredictionUncertainty(value=raw.uncertainty, method="adapter-provided", interpretation="Adapter-provided uncertainty." if raw.uncertainty is not None else "Backend did not provide uncertainty.", available=raw.uncertainty is not None)
            return PredictionResult(molecule_id=molecule.id, property=property_name, value=value, model=raw.model, backend=backend, uncertainty=uncertainty, status="PREDICTED" if value is not None else "UNAVAILABLE", source=raw.model, limitations=raw.limitations)
        except Exception as exc: return PredictionResult(molecule_id=molecule.id, property=property_name, model=adapter.__class__.__name__, backend=backend, status="FAILED", source=adapter.__class__.__name__, limitations=[str(exc)])
    def compare_predictions(self, predictions):
        return {"predictions": list(predictions), "status": "COMPUTATIONAL_RESULT", "limitations": ["Comparison does not validate predictions experimentally."]}
