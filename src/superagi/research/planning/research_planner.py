from .research_plan import ResearchPlan
from .task_decomposer import ResearchTaskDecomposer
from ..models import ResearchQuestion


class ResearchPlanner:
    def __init__(self, decomposer: ResearchTaskDecomposer | None = None) -> None:
        self.decomposer = decomposer or ResearchTaskDecomposer()

    def create_plan(self, question: ResearchQuestion) -> ResearchPlan:
        return self.decomposer.decompose(question)
