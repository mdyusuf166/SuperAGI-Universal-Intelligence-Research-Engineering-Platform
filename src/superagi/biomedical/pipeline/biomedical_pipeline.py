from __future__ import annotations
from dataclasses import dataclass
from superagi.core.events import EventBus
from superagi.core.models import Event, EventType
from superagi.memory import UniversalMemory
from superagi.research.models import ResearchQuestion, ResearchRun, ResearchRunStatus, utc_now
from superagi.research.pipeline import ResearchPipeline
from ..chemistry import ChemistryEngine
from ..dna import DNASequenceAnalyzer
from ..models import Molecule
from ..molecular import MolecularEngine

@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool; reason: str; risk_level: str; limitations: list[str]

class BiomedicalResearchPipeline:
    stages = ("question_analysis", "literature_context", "biomedical_context", "molecular_analysis", "dna_analysis", "chemical_analysis", "prediction", "evidence_evaluation", "hypothesis_generation", "critique", "verification", "report_generation")
    _restricted = ("diagnosis", "treatment", "dosage", "patient-specific", "drug approval", "clinically effective", "safe for humans")
    def __init__(self, memory: UniversalMemory | None = None, event_bus: EventBus | None = None, *, molecular_engine=None, dna_analyzer=None, chemistry_engine=None) -> None:
        self.memory = memory or UniversalMemory(); self.events = event_bus or EventBus(); self.research = ResearchPipeline(memory=self.memory, event_bus=self.events); self.molecular = molecular_engine or MolecularEngine(); self.dna = dna_analyzer or DNASequenceAnalyzer(); self.chemistry = chemistry_engine or ChemistryEngine(); self._cancel_requested = False
    def cancel(self): self._cancel_requested = True; self.research.cancel()
    def safety_decision(self, question: str) -> SafetyDecision:
        if any(term in question.lower() for term in self._restricted): return SafetyDecision(False, "Request requires clinical or patient-specific support outside this computational pipeline.", "high", ["No diagnosis, treatment, dosage, approval, or patient-specific recommendations are produced."])
        return SafetyDecision(True, "Computational biomedical research request is within scope.", "low", ["Outputs remain computational and evidence-grounded."])
    def _event(self, kind, question_id, stage=None): self.events.publish(Event(event_type=kind, task_id=question_id, metadata={"stage": stage} if stage else {}))
    def _save(self, run, stage, artifact):
        run.stage_results[stage] = artifact.model_dump() if hasattr(artifact, "model_dump") else artifact
        self.memory.remember(str(run.stage_results[stage]), source="biomedical_pipeline", source_id=str(run.id), metadata={"stage": stage})
    async def run(self, question: ResearchQuestion, *, smiles: str | None = None, sequence: str | None = None, property_name: str = "unspecified") -> ResearchRun:
        decision = self.safety_decision(question.question); run = ResearchRun(question_id=question.id, status=ResearchRunStatus.RUNNING, started_at=utc_now()); self._event(EventType.BIOMEDICAL_RESEARCH_STARTED, question.id)
        try:
            self._save(run, "question_analysis", {"question": question.model_dump(), "safety": decision.__dict__})
            if not decision.allowed: run.status = ResearchRunStatus.FAILED; run.metadata["safety"] = decision.__dict__; return run
            if self._cancel_requested: raise __import__('asyncio').CancelledError
            base = await self.research.run(question)
            for stage in ("literature_context", "evidence_evaluation", "hypothesis_generation", "critique", "verification", "report_generation"): self._save(run, stage, base.stage_results.get({"literature_context":"literature_review", "evidence_evaluation":"evidence_evaluation", "hypothesis_generation":"hypothesis_generation", "critique":"hypothesis_critique", "verification":"verification", "report_generation":"report_generation"}[stage], {}))
            self._save(run, "biomedical_context", {"classification": "EVIDENCE", "evidence_count": len(base.stage_results.get("evidence_collection", []))})
            if smiles:
                v = self.molecular.validate(smiles); self._save(run, "molecular_analysis", {"classification": "COMPUTATIONAL_RESULT", "validation": v.model_dump(), "descriptors": self.molecular.descriptors(smiles).model_dump() if v.valid else None}); self._event(EventType.MOLECULAR_ANALYSIS_COMPLETED, question.id, "molecular_analysis")
                prediction = self.chemistry.predict_property(Molecule(smiles=smiles), property_name)
                self._save(run, "chemical_analysis", {"classification":"COMPUTATIONAL_RESULT", "status": prediction.status})
                self._save(run, "prediction", prediction.model_dump())
                self._event(EventType.CHEMISTRY_ANALYSIS_COMPLETED, question.id, "chemical_analysis")
            if sequence:
                valid = self.dna.validate(sequence); self._save(run, "dna_analysis", {"classification":"COMPUTATIONAL_RESULT", "validation":valid.model_dump(), "gc_content": self.dna.gc_content(sequence).model_dump() if valid.valid else None}); self._event(EventType.DNA_ANALYSIS_COMPLETED, question.id, "dna_analysis")
            run.verification = base.verification; run.metrics = self.metrics(run); run.status = ResearchRunStatus.COMPLETED; run.completed_at = utc_now(); self._event(EventType.BIOMEDICAL_RESEARCH_COMPLETED, question.id); return run
        except __import__('asyncio').CancelledError:
            run.status = ResearchRunStatus.CANCELLED; run.completed_at = utc_now(); return run
        except Exception as exc:
            run.status = ResearchRunStatus.FAILED; run.completed_at = utc_now(); run.metadata["error"] = str(exc); self._event(EventType.BIOMEDICAL_RESEARCH_FAILED, question.id); return run
    @staticmethod
    def metrics(run: ResearchRun) -> dict[str, float]:
        stages = run.stage_results; values = list(stages.values()); has_prediction = float("prediction" in stages); evidence = float(bool(stages.get("biomedical_context", {}).get("evidence_count", 0))); provenance = float(bool(stages)); uncertainty = float(bool(stages.get("prediction", {}).get("uncertainty")))
        return {"EvidenceCoverage": evidence, "PredictionCoverage": has_prediction, "ProvenanceCompleteness": provenance, "UncertaintyCoverage": uncertainty, "VerificationCoverage": float("verification" in stages), "SafetyCompliance": 1.0}
