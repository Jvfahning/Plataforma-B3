from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from pymongo.collection import Collection
from bson import ObjectId
import re
from datetime import datetime
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlowStep(BaseModel):
    system_prompt: str = Field(..., min_length=1)
    step_name: str = Field(..., min_length=1)
    step_order: int = Field(..., ge=1)
    max_tokens: Optional[int] = Field(default=100, ge=1)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)

    @validator('step_name')
    def validate_step_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\s\-]+$', v):
            raise ValueError('O nome do passo deve conter apenas letras, números, espaços, underscores e hífens')
        return v

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

class FlowManager:
    def __init__(self, collection: Collection):
        self.collection = collection

    def validate_step_orders(self, steps: List[FlowStep]):
        """Valida a ordem dos passos para garantir que são únicas e sequenciais."""
        step_orders = [step.step_order for step in steps]
        if len(set(step_orders)) != len(step_orders):
            raise ValueError("Ordens de passos devem ser únicas")
        if sorted(step_orders) != list(range(1, len(step_orders) + 1)):
            raise ValueError("Ordens de passos devem ser sequenciais começando de 1")

    def create_flow(self, flow_id: str, flow: Flow) -> Flow:
        """Cria um novo fluxo."""
        logger.info(f"Tentando criar fluxo com ID: {flow_id}")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', flow_id):
            raise ValueError('O ID do fluxo deve conter apenas letras, números e underscores')
        
        if self.collection.find_one({"_id": flow_id}):
            raise ValueError(f"Fluxo com ID {flow_id} já existe")
        
        self.validate_step_orders(flow.steps)
        
        flow_dict = {
            "_id": flow_id,
            "name": flow.name,
            "description": flow.description,
            "steps": [step.dict() for step in flow.steps],
            "is_active": flow.is_active,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        self.collection.insert_one(flow_dict)
        logger.info(f"Fluxo criado com sucesso: {flow_id}")
        return flow

    def get_flow(self, flow_id: str) -> Flow:
        """Obtém um fluxo pelo ID."""
        logger.info(f"Obtendo fluxo com ID: {flow_id}")
        flow_dict = self.collection.find_one({"_id": flow_id})
        if not flow_dict:
            raise ValueError(f"Fluxo com ID {flow_id} não encontrado")
        
        return Flow(
            name=flow_dict["name"],
            description=flow_dict["description"],
            steps=[FlowStep(**step) for step in flow_dict["steps"]],
            is_active=flow_dict["is_active"]
        )

    def update_flow(self, flow_id: str, flow: Flow) -> Flow:
        """Atualiza um fluxo existente."""
        logger.info(f"Tentando atualizar fluxo com ID: {flow_id}")
        
        if not self.collection.find_one({"_id": flow_id}):
            raise ValueError(f"Fluxo com ID {flow_id} não encontrado")
        
        self.validate_step_orders(flow.steps)
        
        flow_dict = {
            "name": flow.name,
            "description": flow.description,
            "steps": [step.dict() for step in flow.steps],
            "is_active": flow.is_active,
            "updated_at": datetime.utcnow()
        }
        
        self.collection.update_one(
            {"_id": flow_id},
            {"$set": flow_dict}
        )
        
        logger.info(f"Fluxo atualizado com sucesso: {flow_id}")
        return flow

    def delete_flow(self, flow_id: str):
        """Remove um fluxo."""
        logger.info(f"Tentando excluir fluxo com ID: {flow_id}")
        result = self.collection.delete_one({"_id": flow_id})
        if result.deleted_count == 0:
            raise ValueError(f"Fluxo com ID {flow_id} não encontrado")
        logger.info(f"Fluxo excluído com sucesso: {flow_id}")

    def list_flows(self) -> List[Dict[str, Any]]:
        """Lista todos os fluxos."""
        logger.info("Listando todos os fluxos")
        flows = self.collection.find()
        return [
            {
                "id": flow["_id"],
                "name": flow["name"],
                "description": flow["description"],
                "steps_count": len(flow["steps"]),
                "is_active": flow["is_active"]
            }
            for flow in flows
        ]