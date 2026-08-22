from ..models import ResearchQuestion
from .models import Hypothesis


class HypothesisGenerator:
    def generate(self, question: ResearchQuestion, evidence_ids=()) -> list[Hypothesis]:
        return [Hypothesis(statement=f"The measurable factors identified for '{question.question}' explain variation in the outcome.", rationale="Generated as a proposal from the research question; it is not a scientific truth.", predictions=("Changing a relevant factor changes the measured outcome.",), evidence_ids=tuple(evidence_ids))]
