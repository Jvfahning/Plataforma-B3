from typing import Optional, Dict, List
from pydantic import BaseModel

class FlowStep(BaseModel):
    step_name: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    system_prompt: Optional[str] = None
    max_tokens: Optional[int] = None
    step_order: Optional[int] = None
    execute_if: Optional[str] = None
    conditions: Optional[Dict[str, str]] = None

class Flow(BaseModel):
    name: str
    description: str
    steps: List[FlowStep]