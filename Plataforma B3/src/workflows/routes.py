from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from uuid import UUID
from ..auth.security import get_current_user
from ..auth.models import User
from ..database.repositories import workflow_repository
from .models import Workflow, WorkflowCreate, WorkflowUpdate, WorkflowStatus
from .services import (
    create_workflow, get_workflow, update_workflow,
    delete_workflow, list_workflows, execute_workflow
)

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.post("/", response_model=Workflow, status_code=status.HTTP_201_CREATED)
async def create_workflow_route(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_user)
) -> Workflow:
    """
    Cria um novo workflow.
    
    Args:
        workflow_data: Dados do workflow
        current_user: Usuário autenticado
        
    Returns:
        Workflow criado
        
    Raises:
        HTTPException: Se houver erro na criação
    """
    try:
        return await create_workflow(workflow_data, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=List[Workflow])
async def list_workflows_route(
    current_user: User = Depends(get_current_user)
) -> List[Workflow]:
    """
    Lista todos os workflows do usuário.
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        Lista de workflows
    """
    return await list_workflows(current_user.id)

@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow_route(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user)
) -> Workflow:
    """
    Obtém um workflow pelo ID.
    
    Args:
        workflow_id: ID do workflow
        current_user: Usuário autenticado
        
    Returns:
        Workflow encontrado
        
    Raises:
        HTTPException: Se o workflow não for encontrado
    """
    workflow = await get_workflow(workflow_id, current_user.id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow não encontrado"
        )
    return workflow

@router.put("/{workflow_id}", response_model=Workflow)
async def update_workflow_route(
    workflow_id: UUID,
    workflow_data: WorkflowUpdate,
    current_user: User = Depends(get_current_user)
) -> Workflow:
    """
    Atualiza um workflow existente.
    
    Args:
        workflow_id: ID do workflow
        workflow_data: Dados para atualização
        current_user: Usuário autenticado
        
    Returns:
        Workflow atualizado
        
    Raises:
        HTTPException: Se o workflow não for encontrado
    """
    workflow = await update_workflow(workflow_id, workflow_data, current_user.id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow não encontrado"
        )
    return workflow

@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow_route(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Deleta um workflow.
    
    Args:
        workflow_id: ID do workflow
        current_user: Usuário autenticado
        
    Raises:
        HTTPException: Se o workflow não for encontrado
    """
    success = await delete_workflow(workflow_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow não encontrado"
        )

@router.post("/{workflow_id}/execute", response_model=Workflow)
async def execute_workflow_route(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user)
) -> Workflow:
    """
    Executa um workflow.
    
    Args:
        workflow_id: ID do workflow
        current_user: Usuário autenticado
        
    Returns:
        Workflow executado
        
    Raises:
        HTTPException: Se o workflow não for encontrado
    """
    workflow = await execute_workflow(workflow_id, current_user.id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow não encontrado"
        )
    return workflow 