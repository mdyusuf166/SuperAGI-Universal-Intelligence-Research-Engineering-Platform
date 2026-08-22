from .research_plan import ResearchPlan, ResearchStage
from ..models import ResearchQuestion


class ResearchTaskDecomposer:
    def decompose(self, question: ResearchQuestion) -> ResearchPlan:
        subquestions = question.subquestions or (
            "Which variables and mechanisms are relevant?",
            "What predictive approaches and evidence exist?",
            "What uncertainties and confounders remain?",
        )
        stages = tuple(ResearchStage)
        dependencies = {stage.value: tuple(previous.value for previous in stages[:index]) for index, stage in enumerate(stages)}
        return ResearchPlan(research_question_id=question.id, objective=question.question, subquestions=subquestions, stages=stages, dependencies=dependencies, success_criteria=("Every finding has evidence or is marked unknown", "Verification reports unsupported claims"))
