import re

from ..models import MemoryRecord


class PrivacyPolicy:
    _secret_pattern = re.compile(r"(?i)(api[_ -]?key|password|token|credential|secret)\s*[:=]")

    def validate(self, record: MemoryRecord) -> None:
        if self._secret_pattern.search(record.content):
            raise ValueError("Sensitive credentials cannot be stored")

    def is_sensitive(self, record: MemoryRecord) -> bool:
        return bool(record.metadata.get("sensitive")) or bool(self._secret_pattern.search(record.content))
