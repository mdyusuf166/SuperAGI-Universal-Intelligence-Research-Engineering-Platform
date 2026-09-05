from .models import ScientificQuestion
def create_question(question: str, **kwargs) -> ScientificQuestion: return ScientificQuestion(question=question, **kwargs)
