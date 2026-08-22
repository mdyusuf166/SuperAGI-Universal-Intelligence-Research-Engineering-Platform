from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class EntityType(str, Enum):
    CONCEPT = "concept"
    PERSON = "person"
    PLACE = "place"
    ORGANIZATION = "organization"
    OBJECT = "object"
    EVENT = "event"
    UNKNOWN = "unknown"


class Entity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1)
    entity_type: EntityType = EntityType.UNKNOWN
    description: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
