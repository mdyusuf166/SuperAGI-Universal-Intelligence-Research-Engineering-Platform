from pydantic import BaseModel,ConfigDict
class CircuitComponent(BaseModel): model_config=ConfigDict(extra="forbid");identifier:str;kind:str;nodes:list[str]
