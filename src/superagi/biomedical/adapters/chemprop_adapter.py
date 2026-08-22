from __future__ import annotations

from ..models import Molecule, Prediction


class ChempropAdapter:
    def __init__(self) -> None:
        try:
            import chemprop
            self._module = chemprop
        except ImportError:
            self._module = None

    @property
    def available(self) -> bool:
        return self._module is not None

    def molecular_property_prediction(self, molecule: Molecule, property_name: str) -> Prediction:
        return Prediction(prediction_type=property_name, model="ChempropAdapter", input={"smiles": molecule.smiles}, output={}, uncertainty=None, limitations=["No trained Chemprop model was loaded"])

    def available_models(self) -> list[str]:
        return []


class MockChempropAdapter(ChempropAdapter):
    def __init__(self) -> None:
        self._module = None

    def molecular_property_prediction(self, molecule: Molecule, property_name: str) -> Prediction:
        return Prediction(prediction_type=property_name, model="MockChemprop", input={"smiles": molecule.smiles}, output={"value": round(molecule.smiles.count("O") * 0.5, 3)}, uncertainty=0.2, limitations=["Deterministic mock; not experimentally validated"])

    def available_models(self) -> list[str]:
        return ["mock_property_model"]
