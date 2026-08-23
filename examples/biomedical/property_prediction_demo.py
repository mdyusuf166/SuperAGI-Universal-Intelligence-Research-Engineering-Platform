from superagi.biomedical import Molecule
from superagi.biomedical.chemistry import ChemistryEngine
print("COMPUTATIONAL PROPERTY PREDICTION")
result = ChemistryEngine().predict_property(Molecule(smiles="CCO"), "solubility")
print(result.model_dump())
