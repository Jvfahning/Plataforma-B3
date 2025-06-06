from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import asyncio
from models import Flow
from dotenv import load_dotenv
from flow_manager import FlowManager, Flow
from model_integration import ModelIntegration
from config import settings
from database import get_db
from fastapi.middleware.cors import CORSMiddleware

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa app FastAPI
app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

class FlowuserMessage(BaseModel):
    user_message: str = Field(..., example="Qual a análise?")

# Rotas
@app.post("/createFlows/", response_model=Dict)
def create_flow(flow: Flow, db=Depends(get_db)):
    manager = FlowManager(db)
    try:
        new_flow = Flow(**flow.dict())
        manager.create_flow(new_flow)
        return {"message": "Fluxo criado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/getFlows/", response_model=List[Dict])
def list_flows(db=Depends(get_db)):
    manager = FlowManager(db)
    return manager.list_flows()

@app.get("/getFlowsById/{flow_id}", response_model=Dict)
def get_flow(flow_id: str, db=Depends(get_db)):
    manager = FlowManager(db)
    flow = manager.get_flow(flow_id)
    if flow is None:
        raise HTTPException(status_code=404, detail="Fluxo não encontrado")
    return flow.dict()

@app.put("/updateFlows/{flow_id}", response_model=Dict)
def update_flow(flow_id: str, flow: Flow, db=Depends(get_db)):
    manager = FlowManager(db)
    try:
        updated_flow = Flow(**flow.dict())
        manager.update_flow(flow_id, updated_flow)
        return {"message": "Fluxo atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/deleteFlows/{flow_id}", response_model=Dict)
def delete_flow(flow_id: str, db=Depends(get_db)):
    manager = FlowManager(db)
    try:
        manager.delete_flow(flow_id)
        return {"message": "Fluxo deletado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/flows/{flow_id}/exec_flow", response_model=Dict)
def exec_flow(flow_id: str, request: FlowuserMessage, db=Depends(get_db)):
    manager = FlowManager(db)
    flow = manager.get_flow(flow_id)
    if flow is None:
        raise HTTPException(status_code=404, detail="Fluxo não encontrado")
    
     # Inicializa cliente de modelo
    model_client = ModelIntegration(api_key=settings.UFPB_OPENAI_API_KEY)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            model_client.process_flow(user_message=request.user_message, flow=flow)
        )
        loop.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

