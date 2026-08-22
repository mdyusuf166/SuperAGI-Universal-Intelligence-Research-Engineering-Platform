from __future__ import annotations

from ..models import Document, DocumentChunk


class DocumentChunker:
    def __init__(self, chunk_size: int = 120, overlap: int = 20) -> None:
        if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
            raise ValueError("chunk_size must be positive and overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: Document) -> list[DocumentChunk]:
        words = document.content.split()
        chunks = []
        start = 0
        position = 0
        while start < len(words):
            selected = words[start:start + self.chunk_size]
            chunks.append(DocumentChunk(document_id=document.id, content=" ".join(selected), position=position, token_estimate=len(selected)))
            if start + self.chunk_size >= len(words):
                break
            start += self.chunk_size - self.overlap
            position += 1
        return chunks
