from __future__ import annotations

from superagi.research.experiments import ExperimentDesigner
from superagi.research.hypotheses import HypothesisGenerator
from superagi.research.models import ResearchQuestion


def main() -> None:
    question = ResearchQuestion(question="Does panel orientation affect predicted satellite solar power output?", domain="space")
    hypothesis = HypothesisGenerator().generate(question)[0]
    proposal = ExperimentDesigner().design(question, hypothesis)
    print("PROPOSED HYPOTHESIS")
    print(f"Statement: {hypothesis.statement}")
    print(f"Predictions: {list(hypothesis.predictions)}")
    print(f"Required variables: {[variable.name for variable in proposal.variables]}")
    print(f"Confounders: {[variable.name for variable in proposal.variables if variable.variable_class.value == 'confounding']}")
    print(f"Experiment proposal: {proposal.procedure}")
    print("Verification requirements: collect repeated measurements, preserve raw data, and evaluate uncertainty.")
    print("Status: Proposed only; no experiment was executed or experimentally proven.")


if __name__ == "__main__":
    main()
