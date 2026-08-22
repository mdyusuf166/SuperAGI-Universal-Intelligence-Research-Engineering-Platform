from __future__ import annotations

import asyncio

from superagi.research import ResearchQuestion
from superagi.research.pipeline import ResearchPipeline


async def main() -> None:
    question = ResearchQuestion(question="What variables should be considered when predicting satellite power output?", domain="space", objectives=("Identify measurable predictors",))
    pipeline = ResearchPipeline()
    run = await pipeline.run(question)
    evidence = run.stage_results["evidence_collection"]
    hypotheses = run.stage_results["hypothesis_generation"]
    critiques = run.stage_results["hypothesis_critique"]
    experiment = run.stage_results["experiment_design"][0]
    print(f"Research Run ID: {run.id}")
    print(f"Question: {question.question}")
    print(f"Research stages: {', '.join(run.stage_results)}")
    print(f"Evidence count: {len(evidence)}")
    print(f"Evidence coverage: {run.metrics['EvidenceCoverage']:.2f}")
    print(f"Hypotheses: {len(hypotheses)}")
    print(f"Critiques: {len(critiques)}")
    print(f"Experiment proposal: {experiment['objective']}")
    print(f"Verification status: {run.verification['status']}")
    print(f"Provenance: {len(run.stage_results['report_generation']['provenance'])} references")
    print(f"Limitations: {run.stage_results['report_generation']['limitations']}")


if __name__ == "__main__":
    asyncio.run(main())
