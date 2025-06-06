from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from azure.cosmos import ContainerProxy
import re
from datetime import datetime
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Classe que representa um passo de um fluxo
class FlowStep(BaseModel):
    system_prompt: str = Field(..., min_length=1)
    step_name: str = Field(..., min_length=1)
    step_order: int = Field(..., ge=1)
    max_tokens: Optional[int] = Field(default=100, ge=1)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)
    model: Optional[str] = Field(default="gpt-4o")

    @validator('step_name')
    def validate_step_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\s\-]+$', v):
            raise ValueError('O nome do passo deve conter apenas letras, números, espaços, underscores e hífens')
        return v

# Classe que representa um fluxo
class Flow(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    steps: List[FlowStep] = Field(..., min_items=1)
    is_active: bool = True

    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\s\-]+$', v):
            raise ValueError('O nome do fluxo deve conter apenas letras, números, espaços, underscores e hífens')
        return v

# Classe para gerenciar fluxos
class FlowManager:
    def __init__(self, container: ContainerProxy):
        self.container = container

    def validate_step_orders(self, steps: List[FlowStep]):
        step_orders = [step.step_order for step in steps]
        if len(set(step_orders)) != len(step_orders):
            raise ValueError("Ordens de passos devem ser únicas")
        if sorted(step_orders) != list(range(1, len(step_orders) + 1)):
            raise ValueError("Ordens de passos devem ser sequenciais começando de 1")

    def create_flow(self, flow: Flow) -> Flow:
        self.validate_step_orders(flow.steps)
        flow_dict = {
            "id": str(datetime.utcnow().timestamp()),  # Usando timestamp como ID
            "name": flow.name,
            "description": flow.description,
            "steps": [step.dict() for step in flow.steps],
            "is_active": flow.is_active,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.container.create_item(body=flow_dict)
        return flow

    def get_flow(self, flow_id: str) -> Flow:
        logger.info(f"Obtendo fluxo com ID: {flow_id}")
        query = f"SELECT * FROM c WHERE c.id = '{flow_id}'"
        items = list(self.container.query_items(query=query, enable_cross_partition_query=True))
        if not items:
            raise ValueError(f"Fluxo com ID {flow_id} não encontrado")
        flow_dict = items[0]
        return Flow(
            name=flow_dict["name"],
            description=flow_dict["description"],
            steps=[FlowStep(**step) for step in flow_dict["steps"]],
            is_active=flow_dict["is_active"]
        )

    def update_flow(self, flow_id: str, flow: Flow) -> Flow:
        logger.info(f"Tentando atualizar fluxo com ID: {flow_id}")
        self.validate_step_orders(flow.steps)
        flow_dict = {
            "id": flow_id,
            "name": flow.name,
            "description": flow.description,
            "steps": [step.dict() for step in flow.steps],
            "is_active": flow.is_active,
            "updated_at": datetime.utcnow().isoformat()
        }
        self.container.upsert_item(body=flow_dict)
        logger.info(f"Fluxo atualizado com sucesso: {flow_id}")
        return flow

    def delete_flow(self, flow_id: str):
        logger.info(f"Tentando excluir fluxo com ID: {flow_id}")
        self.container.delete_item(item=flow_id, partition_key=flow_id)
        logger.info(f"Fluxo excluído com sucesso: {flow_id}")

    def list_flows(self) -> List[Dict[str, Any]]:
        logger.info("Listando todos os fluxos")
        query = "SELECT * FROM c"
        flows = list(self.container.query_items(query=query, enable_cross_partition_query=True))
        return [
            {
                "id": flow["id"],
                "name": flow["name"],
                "description": flow["description"],
                "steps_count": len(flow["steps"]),
                "is_active": flow["is_active"]
            }
            for flow in flows
        ]