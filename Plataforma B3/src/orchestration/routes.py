from typing import List, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from ..auth.security import get_current_user
from ..auth.models import User
from ..workflows.models import Task
from ..ia_modules.models import TaskResult
from .services import OrchestrationService

router = APIRouter(prefix="/orchestration", tags=["orchestration"])
service = OrchestrationService()

@router.post("/workflows", response_model=UUID)
async def create_workflow(
    tasks: List[Task],
    current_user: User = Depends(get_current_user)
) -> UUID:
    """
    Cria um novo workflow.
    
    Args:
        tasks: Lista de tarefas do workflow
        current_user: Usuário autenticado
        
    Returns:
        ID do workflow criado
    """
    try:
        return await service.create_workflow(tasks, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/workflows/{workflow_id}/tasks", response_model=List[Task])
async def get_workflow_tasks(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user)
) -> List[Task]:
    """
    Obtém as tarefas de um workflow.
    
    Args:
        workflow_id: ID do workflow
        current_user: Usuário autenticado
        
    Returns:
        Lista de tarefas do workflow
    """
    try:
        return await service.get_workflow_tasks(workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/workflows/{workflow_id}")
async def update_workflow(
    workflow_id: UUID,
    tasks: List[Task],
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Atualiza as tarefas de um workflow.
    
    Args:
        workflow_id: ID do workflow
        tasks: Nova lista de tarefas
        current_user: Usuário autenticado
    """
    try:
        await service.update_workflow(workflow_id, tasks)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/workflows/{workflow_id}")
async def delete_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Remove um workflow.
    
    Args:
        workflow_id: ID do workflow
        current_user: Usuário autenticado
    """
    await service.delete_workflow(workflow_id)

@router.post("/workflows/{workflow_id}/execute", response_model=Dict[str, TaskResult])
async def execute_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user)
) -> Dict[str, TaskResult]:
    """
    Executa um workflow.
    
    Args:
        workflow_id: ID do workflow
        current_user: Usuário autenticado
        
    Returns:
        Dicionário com os resultados de cada tarefa
    """
    try:
        return await service.execute_workflow(workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/workflows/{workflow_id}/visualize", response_model=str)
async def visualize_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user)
) -> str:
    """
    Gera uma visualização do workflow.
    
    Args:
        workflow_id: ID do workflow
        current_user: Usuário autenticado
        
    Returns:
        String com a visualização em formato DOT
    """
    try:
        return await service.visualize_workflow(workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/workflows/{workflow_id}/status", response_model=Dict[str, int])
async def get_workflow_status(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user)
) -> Dict[str, int]:
    """
    Obtém o status atual do workflow.
    
    Args:
        workflow_id: ID do workflow
        current_user: Usuário autenticado
        
    Returns:
        Dicionário com contagem de tarefas por status
    """
    try:
        return await service.get_workflow_status(workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/workflows/{workflow_id}/history", response_model=List[Dict])
async def get_execution_history(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """
    Obtém o histórico de execução de um workflow.
    
    Args:
        workflow_id: ID do workflow
        current_user: Usuário autenticado
        
    Returns:
        Lista de registros de execução
    """
    try:
        return await service.get_execution_history(workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/workflows/{workflow_id}/cleanup")
async def cleanup_workflow_execution(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Limpa os recursos de execução de um workflow.
    
    Args:
        workflow_id: ID do workflow
        current_user: Usuário autenticado
    """
    await service.cleanup_workflow_execution(workflow_id) 