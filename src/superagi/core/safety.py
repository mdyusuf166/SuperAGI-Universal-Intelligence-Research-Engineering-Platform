from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .tools import PermissionLevel


@dataclass(frozen=True)
class ApprovalRequest:
    tool_name: str
    risk_level: str
    reason: str
    request_id: UUID = field(default_factory=uuid4)
    approved: bool = False


class RiskClassifier:
    def classify(self, risk_level: str) -> str:
        return risk_level


class PermissionManager:
    def __init__(self, approvals: set[str] | None = None) -> None:
        self.approvals = approvals or set()

    def authorize(self, tool_name: str, risk_level: str) -> ApprovalRequest | None:
        if risk_level in {PermissionLevel.HIGH_RISK, PermissionLevel.CRITICAL} and tool_name not in self.approvals:
            return ApprovalRequest(tool_name, risk_level, "Explicit approval required")
        return None

    def approve(self, request: ApprovalRequest) -> None:
        self.approvals.add(request.tool_name)


class AuditLogger:
    _sensitive = {"api_key", "password", "token", "credential", "secret"}

    def __init__(self) -> None:
        self.records: list[dict[str, str]] = []

    def log(self, action: str, **fields: object) -> None:
        safe = {key: "[REDACTED]" if key.casefold() in self._sensitive else str(value) for key, value in fields.items()}
        safe.update(action=action, timestamp=datetime.now(timezone.utc).isoformat())
        self.records.append(safe)
