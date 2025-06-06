from pydantic import BaseModel, Field
from typing import List, Optional

class FlowStep(BaseModel):
    """Modelo para representar um passo de um fluxo"""
    step_name: str = Field(..., min_length=1)
    step_order: int = Field(..., ge=1)
    system_prompt: str = Field(..., min_length=1)
    model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=100, ge=1)

class Flow(BaseModel):
    """Modelo para representar um fluxo de processamento"""
    id: str
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    is_active: bool = True
    steps: List[FlowStep] = Field(..., min_items=1)