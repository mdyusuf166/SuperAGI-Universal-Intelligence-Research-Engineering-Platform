import asyncio

import pytest

from superagi.core.models import AgentContext, Task
from superagi.memory import UniversalMemory
from superagi.memory.evidence import Evidence, EvidenceStatus
from superagi.research.agents import CriticAgent, EvidenceAgent, LiteratureAgent, MockLiteratureProvider, SynthesisAgent, VerificationAgent
from superagi.research.agents.critic_agent import Critique
from superagi.research.agents.verification_agent import ResearchVerifier
from superagi.research.evaluation import EvidenceEvaluator, ResearchEvaluator, calculate_metrics
from superagi.research.experiments import ExperimentDesigner, VariableClass
from superagi.research.hypotheses import HypothesisEvaluator, HypothesisGenerator, HypothesisStatus
from superagi.research.models import ResearchQuestion, ResearchRunStatus
from superagi.research.pipeline import ResearchPipeline
from superagi.research.planning import ResearchPlanner, ResearchTaskDecomposer, ResearchStage
from superagi.research.reports import ReportGenerator


def run(coro):
    return asyncio.run(coro)


def question():
    return ResearchQuestion(question="What variables influence satellite power output?", domain="space", objectives=("Identify measurable predictors",))


def test_question_plan_and_finite_decomposition():
    item = question()
    plan = ResearchTaskDecomposer().decompose(item)
    assert len(plan.stages) == 9
    assert plan.stages[0] is ResearchStage.LITERATURE_REVIEW
    assert ResearchPlanner().create_plan(item).research_question_id == item.id


def test_literature_and_evidence_agents():
    literature = LiteratureAgent(MockLiteratureProvider())
    results = literature.search("satellite power output")
    assert results and {"title", "authors", "year", "source", "identifier", "abstract", "metadata"} <= results[0].keys()
    document = literature.provider.get_document(results[0]["identifier"])
    evidence = EvidenceAgent().extract(document)
    assert evidence and evidence[0].source_id == str(document.id)


def test_evidence_evaluation_and_synthesis():
    evidence = Evidence(claim="irradiance affects output", source="paper", source_type="paper", source_id="p1", excerpt="irradiance", confidence=0.9, status=EvidenceStatus.SUPPORTED)
    assessment = EvidenceEvaluator().evaluate(evidence)
    synthesis = SynthesisAgent().synthesize([evidence])
    assert assessment.score > 0 and assessment.status is EvidenceStatus.SUPPORTED
    assert synthesis.key_findings[0]["evidence_ids"] == [str(evidence.id)]


def test_hypothesis_critique_and_experiment():
    item = HypothesisGenerator().generate(question(), ())[0]
    evaluated = HypothesisEvaluator().evaluate(item)
    critique = CriticAgent().critique(evaluated)
    proposal = ExperimentDesigner().design(question(), evaluated)
    assert evaluated.status is HypothesisStatus.UNKNOWN
    assert isinstance(critique, Critique)
    assert any(variable.variable_class is VariableClass.CONFOUNDING for variable in proposal.variables)


def test_report_verification_and_metrics():
    item = Evidence(claim="power depends on irradiance", source="paper", source_type="paper", source_id="p", excerpt="power depends on irradiance", confidence=0.8, status=EvidenceStatus.SUPPORTED)
    synthesis = SynthesisAgent().synthesize([item])
    report = ReportGenerator().generate(question(), synthesis, evidence=[item])
    verification = ResearchVerifier().verify(evidence=[item], hypotheses=[], report=report, provenance=[object()])
    assert verification.status == "verified"
    metrics = calculate_metrics(evidence_count=1, cited_finding_count=1, provenance_count=4, expected_provenance_count=1, testable_hypothesis_count=1, hypothesis_count=1, contradiction_count=0, claim_count=1, reproducibility_score=0.5)
    assert metrics["ProvenanceCompleteness"] == 1.0


def test_pipeline_success_integrates_arc02_memory():
    memory = UniversalMemory()
    pipeline = ResearchPipeline(memory=memory)
    result = run(pipeline.run(question()))
    assert result.status is ResearchRunStatus.COMPLETED
    assert result.plan_id is not None
    assert result.stage_results["evidence_collection"]
    assert result.verification["status"] == "verified"
    assert memory.search("irradiance")


def test_pipeline_failure_is_explicit():
    class FailingProvider(MockLiteratureProvider):
        def search(self, query):
            raise RuntimeError("controlled provider failure")

    with pytest.raises(RuntimeError, match="controlled provider failure"):
        run(ResearchPipeline(literature_provider=FailingProvider()).run(question()))


def test_pipeline_cancellation_is_explicit():
    pipeline = ResearchPipeline()
    pipeline.cancel()
    with pytest.raises(asyncio.CancelledError):
        run(pipeline.run(question()))
