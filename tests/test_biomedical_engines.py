from superagi.biomedical import Molecule
from superagi.biomedical.adapters import MockDeepChemAdapter, MockChempropAdapter
from superagi.biomedical.chemistry import ChemistryEngine
from superagi.biomedical.dna import DNASequenceAnalyzer
from superagi.biomedical.drug_discovery import DrugCandidate, CandidateRanking
from superagi.biomedical.molecular import MolecularEngine

def test_dna_analysis_and_invalid_input():
    dna = DNASequenceAnalyzer(); assert dna.validate("atgc").normalized_value == "ATGC"; assert not dna.validate("ATGCXYZ").valid
    assert dna.gc_content("ATGCGCTA").gc_content == 0.5; assert dna.base_frequency("ATGCGCTA").frequencies == {"A": 2, "T": 2, "G": 2, "C": 2}
    assert dna.reverse_complement("ATGC") == "GCAT"; assert dna.find_motif("ATATAT", "AT").positions == [0, 2, 4]

def test_molecular_unavailable_is_structured():
    engine = MolecularEngine(); result = engine.validate("CCO")
    assert result.adapter_status in {"AVAILABLE", "UNAVAILABLE"}

def test_mock_prediction_and_candidate_ranking():
    molecule = Molecule(smiles="CCO"); engine = ChemistryEngine(deepchem_adapter=MockDeepChemAdapter(), chemprop_adapter=MockChempropAdapter())
    result = engine.predict_property(molecule, "property"); assert result.status == "PREDICTED"; assert result.uncertainty.available
    first = DrugCandidate(molecule_id=molecule.id, molecular_properties={"score": 1}); second = DrugCandidate(molecule_id=molecule.id, molecular_properties={"score": 2})
    assert CandidateRanking().rank([first, second], {"score": 1})[0]["candidate"] == second
