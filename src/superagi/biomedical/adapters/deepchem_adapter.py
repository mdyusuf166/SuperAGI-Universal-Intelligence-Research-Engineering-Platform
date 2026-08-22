from __future__ import annotations

from typing import Any

from ..models import Molecule, Prediction


class DeepChemAdapter:
    def __init__(self) -> None:
        try:
            import deepchem
            self._module = deepchem
        except ImportError:
            self._module = None

    @property
    def available(self) -> bool:
        return self._module is not None

    def featurize_molecule(self, molecule: Molecule) -> dict[str, Any]:
        if not self.available:
            return {"available": False, "error": "DeepChem is unavailable; no features were generated"}
        return {"available": True, "features": self._module.feat.CircularFingerprint(size=128).featurize([molecule.smiles]).tolist()}

    def predict_property(self, molecule: Molecule, property_name: str) -> Prediction:
        return Prediction(prediction_type=property_name, model="DeepChemAdapter", input={"smiles": molecule.smiles}, output={}, uncertainty=None, limitations=["No model download or inference is configured"])

    def available_models(self) -> list[str]:
        return []


class MockDeepChemAdapter(DeepChemAdapter):
    def __init__(self) -> None:
        self._module = None

    def featurize_molecule(self, molecule: Molecule) -> dict[str, Any]:
        return {"available": True, "features": [molecule.smiles.count("C"), len(molecule.smiles)]}

    def predict_property(self, molecule: Molecule, property_name: str) -> Prediction:
        return Prediction(prediction_type=property_name, model="MockDeepChem", input={"smiles": molecule.smiles}, output={"value": float(len(molecule.smiles))}, uncertainty=0.25, limitations=["Deterministic mock; not experimentally validated"])

    def available_models(self) -> list[str]:
        return ["mock_property_model"]
