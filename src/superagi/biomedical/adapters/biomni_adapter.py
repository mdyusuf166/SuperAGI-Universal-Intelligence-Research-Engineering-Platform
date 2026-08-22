from __future__ import annotations

from typing import Any


class BiomniAdapter:
    def __init__(self) -> None:
        self.available = False

    def research_question(self, question: str) -> dict[str, Any]:
        return {"available": self.available, "question": question, "error": "Biomni external orchestration is not enabled"}

    def retrieve_context(self, question: str) -> dict[str, Any]:
        return self.research_question(question)

    def analyze_biomedical_topic(self, question: str) -> dict[str, Any]:
        return self.research_question(question)


class MockBiomniAdapter(BiomniAdapter):
    def __init__(self) -> None:
        self.available = True

    def research_question(self, question: str) -> dict[str, Any]:
        return {"available": True, "question": question, "classification": "RESEARCH_QUESTION", "limitations": ["Controlled mock response; no clinical interpretation"]}
