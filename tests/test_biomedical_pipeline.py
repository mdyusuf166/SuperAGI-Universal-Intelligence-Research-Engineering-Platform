import asyncio
from superagi.biomedical.pipeline import BiomedicalResearchPipeline
from superagi.research.models import ResearchQuestion, ResearchRunStatus

def test_pipeline_rejects_clinical_request():
    pipeline = BiomedicalResearchPipeline(); run = asyncio.run(pipeline.run(ResearchQuestion(question="Give a patient-specific treatment dosage")))
    assert run.status == ResearchRunStatus.FAILED and run.metadata["safety"]["allowed"] is False

def test_pipeline_has_explicit_computational_stages():
    pipeline = BiomedicalResearchPipeline(); run = asyncio.run(pipeline.run(ResearchQuestion(question="How can computational molecular analysis prioritize research?"), smiles="CCO", sequence="ATGC"))
    assert run.status == ResearchRunStatus.COMPLETED
    assert {"question_analysis", "molecular_analysis", "dna_analysis", "prediction", "verification"} <= set(run.stage_results)
    assert run.metrics["SafetyCompliance"] == 1.0
