from datetime import datetime, timedelta, timezone

from ..models import MemoryRecord


class RetentionPolicy:
    def __init__(self, minimum_days: int = 0) -> None:
        self.minimum_days = minimum_days

    def expires_at(self, record: MemoryRecord) -> datetime:
        return record.created_at + timedelta(days=self.minimum_days)

    def can_delete(self, record: MemoryRecord, now: datetime | None = None) -> bool:
        return (now or datetime.now(timezone.utc)) >= self.expires_at(record)
