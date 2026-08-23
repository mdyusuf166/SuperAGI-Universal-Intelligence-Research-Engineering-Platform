from superagi.biomedical.molecular import MolecularEngine
engine = MolecularEngine(); smiles = "CCO"
print("COMPUTATIONAL MOLECULAR ANALYSIS")
print(engine.validate(smiles).model_dump()); print(engine.descriptors(smiles).model_dump()); print(engine.fingerprint(smiles).model_dump()); print(engine.similarity(smiles, "CCCO").model_dump())
