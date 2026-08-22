from __future__ import annotations

import re
from abc import ABC, abstractmethod


class RankingStrategy:
    """Transparent lexical scorer; this is not semantic or vector search."""

    def score(self, query: str, text: str) -> float:
        query_terms = set(re.findall(r"[\w-]+", query.casefold()))
        text_terms = set(re.findall(r"[\w-]+", text.casefold()))
        if not query_terms:
            return 0.0
        return len(query_terms & text_terms) / len(query_terms)


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Future embedding boundary; no embedding implementation in ARC-02."""


class Reranker(ABC):
    @abstractmethod
    def rerank(self, query: str, results: list[object]) -> list[object]:
        """Future result reranking boundary."""


class WebRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str) -> list[object]:
        """Future web retrieval boundary."""


class PaperRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str) -> list[object]:
        """Future paper retrieval boundary."""
