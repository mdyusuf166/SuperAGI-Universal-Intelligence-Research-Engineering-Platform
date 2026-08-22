from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class RelationType(str, Enum):
    IS_A = "is_a"
    PART_OF = "part_of"
    CAUSES = "causes"
    RELATED_TO = "related_to"
    DEPENDS_ON = "depends_on"
    USES = "uses"
    PRODUCES = "produces"
    MEASURED_BY = "measured_by"
    LOCATED_IN = "located_in"
    STUDIES = "studies"
    TREATS = "treats"
    INTERACTS_WITH = "interacts_with"


class Relation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID = Field(default_factory=uuid4)
    source_entity_id: UUID
    target_entity_id: UUID
    relation_type: RelationType
    confidence: float = Field(default=0.5, ge=0, le=1)
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)
