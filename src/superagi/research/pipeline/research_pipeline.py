from __future__ import annotations

import asyncio
from datetime import timezone
from typing import Any

from superagi.core.events import EventBus
from superagi.core.models import Event, EventType, Task
from superagi.memory import Document, SourceType, UniversalMemory
from superagi.memory.evidence import Evidence
from superagi.memory.workflow import ResearchContextWorkflow

from ..agents import CriticAgent, EvidenceAgent, LiteratureAgent, MockLiteratureProvider, SynthesisAgent, VerificationAgent
from ..agents.critic_agent import Critique
from ..agents.verification_agent import ResearchVerifier
from ..evaluation.evaluator import EvidenceAssessment, EvidenceEvaluator, ResearchEvaluator
from ..experiments import ExperimentDesigner
from ..hypotheses import HypothesisEvaluator, HypothesisGenerator
from ..models import ResearchQuestion, ResearchRun, ResearchRunStatus, utc_now
from ..planning import ResearchPlanner
from ..reports import ReportGenerator, ResearchReport


class ResearchPipeline:
    def __init__(self, memory: UniversalMemory | None = None, literature_provider=None, event_bus: EventBus | None = None) -> None:
        self.memory = memory or UniversalMemory()
        self.literature = LiteratureAgent(literature_provider or MockLiteratureProvider())
        self.evidence_agent = EvidenceAgent()
        self.evidence_evaluator = EvidenceEvaluator()
        self.synthesis_agent = SynthesisAgent()
        self.hypothesis_generator = HypothesisGenerator()
        self.hypothesis_evaluator = HypothesisEvaluator()
        self.critic = CriticAgent()
        self.experiment_designer = ExperimentDesigner()
        self.verifier = ResearchVerifier()
        self.report_generator = ReportGenerator()
        self.evaluator = ResearchEvaluator()
        self.events = event_bus or EventBus()
        self._cancel_requested = False

    def cancel(self) -> None:
        self._cancel_requested = True

    async def run(self, question: ResearchQuestion) -> ResearchRun:
        run = ResearchRun(question_id=question.id, status=ResearchRunStatus.RUNNING, started_at=utc_now())
        task = Task(description=question.question)
        try:
            plan = ResearchPlanner().create_plan(question)
            run.plan_id = plan.id
            self._stage(run, "research_plan", plan)
            self._check_cancel(run)
            literature = self.literature.search(question.question)
            documents = [self.literature.provider.get_document(item["identifier"]) for item in literature]
            documents = [document for document in documents if document is not None]
            for document in documents:
                self.memory.ingest_document(document)
            self._stage(run, "literature_review", literature)
            evidence = [item for document in documents for item in self.evidence_agent.extract(document)]
            evidence = [self.memory.add_evidence(item) for item in evidence]
            self._stage(run, "evidence_collection", evidence)
            assessments = [self.evidence_evaluator.evaluate(item) for item in evidence]
            self._stage(run, "evidence_evaluation", assessments)
            synthesis = self.synthesis_agent.synthesize(evidence)
            self._stage(run, "knowledge_synthesis", synthesis)
            hypotheses = [self.hypothesis_evaluator.evaluate(item, synthesis.evidence_ids) for item in self.hypothesis_generator.generate(question, synthesis.evidence_ids)]
            self._stage(run, "hypothesis_generation", hypotheses)
            critiques = [self.critic.critique(item) for item in hypotheses]
            self._stage(run, "hypothesis_critique", critiques)
            experiments = [self.experiment_designer.design(question, item) for item in hypotheses]
            self._stage(run, "experiment_design", experiments)
            report = self.report_generator.generate(question, synthesis, evidence=evidence, hypotheses=hypotheses, critiques=critiques, experiments=experiments, provenance=[str(item.id) for item in self.memory.provenance.records])
            verification = self.verifier.verify(evidence=evidence, hypotheses=hypotheses, report=report, provenance=self.memory.provenance.records)
            run.verification = verification.model_dump()
            self._stage(run, "verification", verification)
            report = self.report_generator.generate(question, synthesis, evidence=evidence, hypotheses=hypotheses, critiques=critiques, experiments=experiments, verification=verification, provenance=[str(item.id) for item in self.memory.provenance.records])
            self._stage(run, "report_generation", report)
            run.metrics = self.evaluator.evaluate(report, evidence_count=len(evidence), hypotheses=hypotheses, provenance_count=len(self.memory.provenance.records))
            run.stage_results["evidence_assessments"] = [item.model_dump() for item in assessments]
            self._persist(run, question, plan, evidence, synthesis, hypotheses, critiques, experiments, verification, report)
            run.status = ResearchRunStatus.COMPLETED
            run.completed_at = utc_now()
            return run
        except asyncio.CancelledError:
            run.status = ResearchRunStatus.CANCELLED
            run.completed_at = utc_now()
            raise
        except Exception as exc:
            run.status = ResearchRunStatus.FAILED
            run.completed_at = utc_now()
            run.metadata["error"] = str(exc)
            raise

    def _stage(self, run: ResearchRun, name: str, artifact: Any) -> None:
        self._check_cancel(run)
        run.stage_results[name] = [item.model_dump() if hasattr(item, "model_dump") else item for item in artifact] if isinstance(artifact, list) else (artifact.model_dump() if hasattr(artifact, "model_dump") else artifact)
        event_type = EventType.PLAN_STARTED if name == "research_plan" else EventType.AGENT_COMPLETED
        self.events.publish(Event(event_type=event_type, task_id=run.question_id, metadata={"stage": name}))

    def _check_cancel(self, run: ResearchRun) -> None:
        if self._cancel_requested:
            run.status = ResearchRunStatus.CANCELLED
            raise asyncio.CancelledError

    def _persist(self, run, question, plan, evidence, synthesis, hypotheses, critiques, experiments, verification, report) -> None:
        artifacts = [("question", question), ("plan", plan), ("evidence", evidence), ("synthesis", synthesis), ("hypotheses", hypotheses), ("critiques", critiques), ("experiments", experiments), ("verification", verification), ("report", report)]
        for name, artifact in artifacts:
            payload = [item.model_dump() if hasattr(item, "model_dump") else item for item in artifact] if isinstance(artifact, list) else artifact.model_dump()
            self.memory.remember(str(payload), source="research_pipeline", source_id=str(run.id), metadata={"artifact": name, "run_id": str(run.id)})
