from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any


class ModelProvider:
    async def generate(self, prompt: str, **options: Any) -> str:
        raise NotImplementedError

    async def stream(self, prompt: str, **options: Any) -> AsyncIterator[str]:
        raise NotImplementedError


class MockModelProvider(ModelProvider):
    async def generate(self, prompt: str, **_: Any) -> str:
        return f"Mock response for: {prompt}"

    async def stream(self, prompt: str, **options: Any) -> AsyncIterator[str]:
        yield await self.generate(prompt, **options)
