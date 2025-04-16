from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from pymongo.collection import Collection
from bson import ObjectId
import re
from datetime import datetime

class FlowStep(BaseModel):
    system_prompt: str = Field(..., min_length=1)
    step_name: str = Field(..., min_length=1)
    step_order: int = Field(..., ge=1)

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

    def create_flow(self, flow_id: str, flow: Flow) -> Flow:
        """Cria um novo fluxo"""
        # Validação do ID
        if not re.match(r'^[a-zA-Z0-9_]+$', flow_id):
            raise ValueError('O ID do fluxo deve conter apenas letras, números e underscores')
        
        # Verifica se o fluxo já existe
        if self.collection.find_one({"_id": flow_id}):
            raise ValueError(f"Fluxo com ID {flow_id} já existe")
        
        # Valida a ordem dos passos
        step_orders = [step.step_order for step in flow.steps]
        if len(set(step_orders)) != len(step_orders):
            raise ValueError("Ordens de passos devem ser únicas")
        if sorted(step_orders) != list(range(1, len(step_orders) + 1)):
            raise ValueError("Ordens de passos devem ser sequenciais começando de 1")
        
        # Cria o fluxo no banco
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
        return flow

    def get_flow(self, flow_id: str) -> Flow:
        """Obtém um fluxo pelo ID"""
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
        """Atualiza um fluxo existente"""
        # Verifica se o fluxo existe
        if not self.collection.find_one({"_id": flow_id}):
            raise ValueError(f"Fluxo com ID {flow_id} não encontrado")
        
        # Valida a ordem dos passos
        step_orders = [step.step_order for step in flow.steps]
        if len(set(step_orders)) != len(step_orders):
            raise ValueError("Ordens de passos devem ser únicas")
        if sorted(step_orders) != list(range(1, len(step_orders) + 1)):
            raise ValueError("Ordens de passos devem ser sequenciais começando de 1")
        
        # Atualiza o fluxo
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
        
        return flow

    def delete_flow(self, flow_id: str):
        """Remove um fluxo"""
        result = self.collection.delete_one({"_id": flow_id})
        if result.deleted_count == 0:
            raise ValueError(f"Fluxo com ID {flow_id} não encontrado")

    def list_flows(self) -> List[Dict[str, Any]]:
        """Lista todos os fluxos"""
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