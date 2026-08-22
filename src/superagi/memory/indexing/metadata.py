from typing import Any

from ..models import Document, DocumentChunk


def source_metadata(document: Document, chunk: DocumentChunk | None = None) -> dict[str, Any]:
    metadata: dict[str, Any] = {"source": document.source, "source_type": document.source_type.value, "document_id": str(document.id)}
    if chunk is not None:
        metadata["chunk_id"] = str(chunk.id)
        metadata["position"] = chunk.position
    return metadata
