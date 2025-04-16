from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

from .model_integration import ModelIntegration
from .flow_manager import Flow, FlowStep, FlowManager

# Carrega variáveis de ambiente
load_dotenv()

app = FastAPI(
    title="Plataforma B3 - API de Integração com IA",
    description="API para integração com modelos de IA da B3",
    version="1.0.0"
)

# Inicializa o cliente de integração com o modelo
model_client = ModelIntegration(
    api_key=os.getenv("API_KEY"),
    model_url=os.getenv("MODEL_URL")
)

# Inicializa o gerenciador de fluxos
flow_manager = FlowManager()

class Message(BaseModel):
    content: str
    role: str

class ChatRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 0.7
    model: str = "gpt4o"
    top_p: Optional[float] = 0.9
    frequency_penalty: Optional[float] = 1.0
    presence_penalty: Optional[float] = 0.5
    max_tokens: Optional[int] = 3000
    stop: Optional[str] = "\n"

class FlowStepRequest(BaseModel):
    system_prompt: str
    step_name: str
    step_order: int

class FlowRequest(BaseModel):
    name: str
    description: str
    steps: List[FlowStepRequest]
    is_active: bool = True

class FlowChatRequest(BaseModel):
    user_message: str
    flow_id: str
    temperature: Optional[float] = 0.7
    model: str = "gpt4o"
    top_p: Optional[float] = 0.9
    frequency_penalty: Optional[float] = 1.0
    presence_penalty: Optional[float] = 0.5
    max_tokens: Optional[int] = 3000
    stop: Optional[str] = "\n"

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = await model_client.chat_completion(
            messages=request.messages,
            temperature=request.temperature,
            model=request.model,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
            max_tokens=request.max_tokens,
            stop=request.stop
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/flows")
async def create_flow(flow_id: str, flow: FlowRequest):
    try:
        # Converte FlowStepRequest para FlowStep
        flow_steps = [
            FlowStep(
                system_prompt=step.system_prompt,
                step_name=step.step_name,
                step_order=step.step_order
            )
            for step in flow.steps
        ]
        
        # Cria o fluxo
        created_flow = flow_manager.create_flow(
            flow_id=flow_id,
            flow=Flow(
                name=flow.name,
                description=flow.description,
                steps=flow_steps,
                is_active=flow.is_active
            )
        )
        return {"message": "Fluxo criado com sucesso", "flow": created_flow.dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/flows")
async def list_flows():
    return flow_manager.list_flows()

@app.get("/flows/{flow_id}")
async def get_flow(flow_id: str):
    try:
        return flow_manager.get_flow(flow_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/flows/{flow_id}")
async def update_flow(flow_id: str, flow: FlowRequest):
    try:
        # Converte FlowStepRequest para FlowStep
        flow_steps = [
            FlowStep(
                system_prompt=step.system_prompt,
                step_name=step.step_name,
                step_order=step.step_order
            )
            for step in flow.steps
        ]
        
        # Atualiza o fluxo
        updated_flow = flow_manager.update_flow(
            flow_id=flow_id,
            flow=Flow(
                name=flow.name,
                description=flow.description,
                steps=flow_steps,
                is_active=flow.is_active
            )
        )
        return {"message": "Fluxo atualizado com sucesso", "flow": updated_flow.dict()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/flows/{flow_id}")
async def delete_flow(flow_id: str):
    try:
        flow_manager.delete_flow(flow_id)
        return {"message": "Fluxo deletado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/flows/{flow_id}/chat")
async def chat_with_flow(flow_id: str, request: FlowChatRequest):
    try:
        # Obtém o fluxo
        flow = flow_manager.get_flow(flow_id)
        
        # Processa a mensagem usando o fluxo
        response = await model_client.process_flow(
            user_message=request.user_message,
            flow=flow,
            temperature=request.temperature,
            model=request.model
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 