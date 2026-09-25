from pydantic import BaseModel, ConfigDict, Field

class CircuitComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    identifier: str
    kind: str
    nodes: list[str]
    value: str | float | int | None = None
    terminals: list[str] = Field(default_factory=list)
