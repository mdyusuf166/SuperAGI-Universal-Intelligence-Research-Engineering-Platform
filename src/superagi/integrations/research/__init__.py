from superagi.integrations.base import OptionalIntegrationAdapter, ResearchEngineAdapter


class ResearchAdapter(OptionalIntegrationAdapter, ResearchEngineAdapter):
    def __init__(self) -> None:
        super().__init__('research', ('search', 'retrieve', 'analyze', 'synthesize'))

    def search(self, query: str, **options: object) -> list[dict[str, object]]:
        raise NotImplementedError

    def retrieve(self, reference: str, **options: object) -> dict[str, object]:
        raise NotImplementedError

    def analyze(self, evidence: list[dict[str, object]], **options: object) -> dict[str, object]:
        raise NotImplementedError

    def synthesize(self, analysis: dict[str, object], **options: object) -> dict[str, object]:
        raise NotImplementedError
