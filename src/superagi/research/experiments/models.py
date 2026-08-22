from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class VariableClass(str, Enum):
    INDEPENDENT = "independent"
    DEPENDENT = "dependent"
    CONTROL = "control"
    CONFOUNDING = "confounding"


class Variable(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    variable_class: VariableClass
    measurement: str = ""


class ExperimentProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID = Field(default_factory=uuid4)
    objective: str
    hypothesis: str
    variables: list[Variable] = Field(default_factory=list)
    controls: list[str] = Field(default_factory=list)
    procedure: list[str] = Field(default_factory=list)
    measurements: list[str] = Field(default_factory=list)
    expected_outcomes: list[str] = Field(default_factory=list)
    failure_conditions: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    reproducibility_notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
