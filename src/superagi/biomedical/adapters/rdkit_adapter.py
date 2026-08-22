from __future__ import annotations

from typing import Any


class AdapterResult(dict):
    @property
    def available(self) -> bool:
        return bool(self.get("available", False))


class RDKitAdapter:
    def __init__(self) -> None:
        try:
            from rdkit import Chem, Crippen, Descriptors, Lipinski
            from rdkit.Chem import AllChem
            self._rdkit = (Chem, Crippen, Descriptors, Lipinski, AllChem)
        except ImportError:
            self._rdkit = None

    @property
    def available(self) -> bool:
        return self._rdkit is not None

    def _molecule(self, smiles: str):
        if not self._rdkit:
            return AdapterResult(available=False, error="RDKit is unavailable; chemistry calculations were not performed")
        molecule = self._rdkit[0].MolFromSmiles(smiles)
        if molecule is None:
            return AdapterResult(available=True, error="Invalid SMILES")
        return molecule

    def validate_smiles(self, smiles: str) -> AdapterResult:
        molecule = self._molecule(smiles)
        if isinstance(molecule, dict):
            return molecule
        return AdapterResult(available=True, valid=True)

    def molecular_formula(self, smiles: str) -> AdapterResult:
        molecule = self._molecule(smiles)
        if isinstance(molecule, dict):
            return molecule
        from rdkit.Chem import rdMolDescriptors
        return AdapterResult(available=True, formula=rdMolDescriptors.CalcMolFormula(molecule))

    def molecular_weight(self, smiles: str) -> AdapterResult:
        molecule = self._molecule(smiles)
        if isinstance(molecule, dict):
            return molecule
        return AdapterResult(available=True, value=self._rdkit[2].MolWt(molecule), unit="g/mol")

    def logp(self, smiles: str) -> AdapterResult:
        molecule = self._molecule(smiles)
        if isinstance(molecule, dict):
            return molecule
        return AdapterResult(available=True, value=self._rdkit[1].MolLogP(molecule))

    def fingerprint(self, smiles: str) -> AdapterResult:
        molecule = self._molecule(smiles)
        if isinstance(molecule, dict):
            return molecule
        fingerprint = self._rdkit[4].GetMorganFingerprintAsBitVect(molecule, 2, nBits=128)
        return AdapterResult(available=True, bits=list(fingerprint.ToBitString()))

    def descriptors(self, smiles: str) -> AdapterResult:
        molecule = self._molecule(smiles)
        if isinstance(molecule, dict):
            return molecule
        return AdapterResult(available=True, descriptors={"molecular_weight": self._rdkit[2].MolWt(molecule), "logp": self._rdkit[1].MolLogP(molecule), "h_bond_donors": self._rdkit[3].NumHDonors(molecule), "h_bond_acceptors": self._rdkit[3].NumHAcceptors(molecule)})
