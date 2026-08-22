from superagi.integrations.base import OptionalIntegrationAdapter


class GraphRAGAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('graphrag', ('graph_retrieval', 'knowledge_indexing'))
