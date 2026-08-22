from .models import ResearchReport, ResearchSynthesis


class ReportGenerator:
    def generate(self, question, synthesis: ResearchSynthesis, *, evidence=(), hypotheses=(), critiques=(), experiments=(), verification=None, provenance=()) -> ResearchReport:
        return ResearchReport(research_question=question.question, objectives=list(question.objectives), method=["Controlled local literature corpus", "Deterministic lexical retrieval", "Evidence-first synthesis"], evidence=[item.model_dump() for item in evidence], key_findings=synthesis.key_findings, knowledge_gaps=synthesis.knowledge_gaps, hypotheses=[item.model_dump() for item in hypotheses], critiques=[item.model_dump() if hasattr(item, "model_dump") else item for item in critiques], experiment_proposals=[item.model_dump() for item in experiments], limitations=synthesis.limitations, verification=verification.model_dump() if hasattr(verification, "model_dump") else (verification or {}), provenance=list(provenance))
