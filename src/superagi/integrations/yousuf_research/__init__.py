"""Adapters for Yousuf's existing research projects.

Existing research remains outside the upstream checkouts and is integrated
through explicit boundaries as each project is located and reviewed.
"""

from superagi.integrations.base import OptionalIntegrationAdapter


class CardioAGIXAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('CardioAGI-X', ('cardiovascular_research',))


class DermAIResearchAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('DermAI-Research', ('dermatology_research',))


class MolecularIntelligenceAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('MolecularIntelligence', ('molecular_research',))


class DigitalHumanIntelligenceLabAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('Digital-Human-Intelligence-Lab', ('digital_human_research',))


class SpaceIntelligenceAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('Space Intelligence', ('space_research',))
