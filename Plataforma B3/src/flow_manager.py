from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
import re
from datetime import datetime
import logging
from pymongo.collection import Collection
import uuid
import yaml
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlowStep(BaseModel):
    system_prompt: str = Field(..., min_length=1)
    step_name: str = Field(..., min_length=1)
    step_order: Optional[int] = Field(default=None, ge=1)
    max_tokens: Optional[int] = Field(default=100, ge=1)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)
    model: Optional[str] = Field(default="gpt-4o")
    conditions: Optional[Dict[str, str]] = None
    execute_if: Optional[str] = None

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
        step_orders = [step.step_order for step in steps if step.step_order is not None]
        if len(set(step_orders)) != len(step_orders):
            raise ValueError("Ordens de passos devem ser únicas")
        if sorted(step_orders) != list(range(1, len(step_orders) + 1)):
            raise ValueError("Ordens de passos devem ser sequenciais começando de 1")

    def json_to_yaml(self, json_data: Dict) -> str:
        """Converte JSON para YAML."""
        return yaml.dump(json_data, default_flow_style=False)

    def yaml_to_json(self, yaml_data: str) -> Dict:
        """Converte YAML para JSON."""
        return yaml.safe_load(yaml_data)

    def generate_workflow_id(self) -> str:
        """Gera um identificador único para o workflow."""
        return str(uuid.uuid4())

    def create_flow(self, flow_json: Dict) -> str:
        """Cria um novo workflow a partir de JSON."""
        self.validate_step_orders(flow_json['steps'])
        flow_id = self.generate_workflow_id()
        flow_yaml = self.json_to_yaml(flow_json)
        self.collection.insert_one({"_id": flow_id, "yaml": flow_yaml})
        return flow_id

    def get_flow(self, flow_id: str) -> Dict:
        """Recupera um workflow e converte para JSON."""
        logger.info(f"Obtendo fluxo com ID: {flow_id}")
        flow_doc = self.collection.find_one({"_id": flow_id})
        if not flow_doc:
            raise ValueError(f"Workflow com ID {flow_id} não encontrado")
        return self.yaml_to_json(flow_doc["yaml"])

    def update_flow(self, flow_id: str, flow_json: Dict):
        """Atualiza um workflow existente."""
        self.validate_step_orders(flow_json['steps'])
        flow_yaml = self.json_to_yaml(flow_json)
        result = self.collection.update_one({"_id": flow_id}, {"$set": {"yaml": flow_yaml}})
        if result.matched_count == 0:
            raise ValueError(f"Workflow com ID {flow_id} não encontrado")
        logger.info(f"Fluxo atualizado com sucesso: {flow_id}")

    def delete_flow(self, flow_id: str):
        logger.info(f"Tentando excluir fluxo com ID: {flow_id}")
        result = self.collection.delete_one({"_id": flow_id})
        if result.deleted_count == 0:
            raise ValueError(f"Fluxo com ID {flow_id} não encontrado")
        logger.info(f"Fluxo excluído com sucesso: {flow_id}")

    def list_flows(self) -> List[Dict[str, Any]]:
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

    def execute_flow(self, flow_id: str):
        """Executa um workflow usando Argo."""
        logger.info(f"Executando fluxo com ID: {flow_id}")
        flow_doc = self.collection.find_one({"_id": flow_id})
        if not flow_doc:
            raise ValueError(f"Workflow com ID {flow_id} não encontrado")
        
        yaml_content = flow_doc["yaml"]
        self.submit_workflow(yaml_content)

    def submit_workflow(self, yaml_content: str):
        """Submete um workflow ao Argo."""
        url = "http://argo-server.argo:2746/api/v1/workflows/argo"
        headers = {"Content-Type": "application/yaml"}
        response = requests.post(url, headers=headers, data=yaml_content)
        if response.status_code == 200:
            logger.info("Workflow submetido com sucesso")
        else:
            logger.error(f"Erro ao submeter workflow: {response.text}")

    def process_step(self, step: FlowStep, user_input: str) -> Dict:
        pass

    def get_next_step(self, flow: Flow, current_order: int) -> Optional[FlowStep]:
        return next((step for step in flow.steps if step.step_order == current_order + 1), None)