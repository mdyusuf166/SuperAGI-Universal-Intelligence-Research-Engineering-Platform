from __future__ import annotations

from superagi.core.models import AgentContext, AgentResult, Task
from superagi.memory.evidence import Evidence
from superagi.research.reports.models import ResearchSynthesis

from ._base import ResearchAgent, metadata


class SynthesisAgent(ResearchAgent):
    def __init__(self) -> None:
        super().__init__(metadata("synthesis_agent", "Combines evidence into traceable findings", ("knowledge_synthesis", "evidence_linking")))

    def synthesize(self, evidence: list[Evidence]) -> ResearchSynthesis:
        findings = [{"claim": item.claim, "evidence_ids": [str(item.id)], "classification": "EVIDENCE"} for item in evidence]
        return ResearchSynthesis(summary=f"Synthesized {len(evidence)} source-grounded findings", key_findings=findings, agreements=["The controlled sources identify measurable physical and telemetry variables."], knowledge_gaps=["No live literature search or measured telemetry was used."], limitations=["Lexical controlled corpus only; findings are not independently validated."], evidence_ids=[item.id for item in evidence])

    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        evidence = [Evidence.model_validate(item) if isinstance(item, dict) else item for item in context.values.get("evidence", [])]
        synthesis = self.synthesize(evidence)
        return AgentResult(success=True, confidence=0.8, summary=synthesis.summary, output={"synthesis": synthesis.model_dump()})
