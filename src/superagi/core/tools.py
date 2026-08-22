from __future__ import annotations

import ast
import operator
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from .models import ToolResult


class PermissionLevel(str, Enum):
    READ_ONLY = "read_only"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    CRITICAL = "critical"


class BaseTool(ABC):
    def __init__(self, name: str, description: str, risk_level: PermissionLevel = PermissionLevel.LOW_RISK, permissions: tuple[str, ...] = (), input_schema: dict[str, Any] | None = None, output_schema: dict[str, Any] | None = None) -> None:
        self.id: UUID = uuid4()
        self.name = name
        self.description = description
        self.risk_level = risk_level
        self.permissions = permissions
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}

    @abstractmethod
    async def execute(self, **arguments: Any) -> ToolResult:
        """Execute a tool using validated keyword arguments."""


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        return self._tools[name]

    def unregister(self, name: str) -> BaseTool:
        return self._tools.pop(name)

    def list(self) -> list[BaseTool]:
        return list(self._tools.values())

    def exists(self, name: str) -> bool:
        return name in self._tools


class CalculatorTool(BaseTool):
    def __init__(self) -> None:
        super().__init__("calculator", "Evaluate a basic arithmetic expression", PermissionLevel.READ_ONLY)

    async def execute(self, expression: str, **_: Any) -> ToolResult:
        try:
            value = _safe_math(ast.parse(expression, mode="eval").body)
            return ToolResult(success=True, output={"value": value})
        except (SyntaxError, ValueError, TypeError, ZeroDivisionError) as exc:
            return ToolResult(success=False, error=str(exc))


class TextAnalysisTool(BaseTool):
    def __init__(self) -> None:
        super().__init__("text_analysis", "Return basic text statistics", PermissionLevel.READ_ONLY)

    async def execute(self, text: str, **_: Any) -> ToolResult:
        words = text.split()
        return ToolResult(success=True, output={"characters": len(text), "words": len(words), "lines": len(text.splitlines())})


class SandboxFileReadTool(BaseTool):
    def __init__(self, root: str | Path) -> None:
        super().__init__("sandbox_file_read", "Read text files inside an approved directory", PermissionLevel.READ_ONLY)
        self.root = Path(root).resolve()

    async def execute(self, path: str, **_: Any) -> ToolResult:
        candidate = (self.root / path).resolve()
        try:
            candidate.relative_to(self.root)
            return ToolResult(success=True, output={"content": candidate.read_text(encoding="utf-8")})
        except (OSError, ValueError) as exc:
            return ToolResult(success=False, error=str(exc))


_operators = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Pow: operator.pow}


def _safe_math(node: ast.AST) -> float | int:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _safe_math(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and type(node.op) in _operators:
        return _operators[type(node.op)](_safe_math(node.left), _safe_math(node.right))
    raise ValueError("Only numeric arithmetic is allowed")
