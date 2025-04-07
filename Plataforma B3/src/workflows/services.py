from .models import (
    Workflow, WorkflowCreate, WorkflowUpdate,
    Task, TaskCreate, TaskUpdate,
    WorkflowStatus, TaskStatus, TaskType
)
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from ..database.repositories import workflow_repository
from ..ia_modules.services import (
    execute_chat_task,
    execute_document_processing_task,
    execute_sentiment_analysis_task,
    execute_goal_analysis_task,
    execute_image_generation_task
)

# TODO: Implementar conexão com banco de dados
# Por enquanto, usaremos dicionários em memória para simular o banco de dados
workflows_db = {}
tasks_db = {}

async def create_workflow(workflow_data: WorkflowCreate, user_id: UUID) -> Workflow:
    """
    Cria um novo workflow.
    
    Args:
        workflow_data: Dados do workflow
        user_id: ID do usuário
        
    Returns:
        Workflow criado
    """
    workflow = Workflow(
        name=workflow_data.name,
        description=workflow_data.description,
        tasks=workflow_data.tasks,
        user_id=user_id,
        status=WorkflowStatus.DRAFT
    )
    
    return await workflow_repository.create(workflow)

async def get_workflow(workflow_id: UUID, user_id: UUID) -> Optional[Workflow]:
    """
    Obtém um workflow pelo ID.
    
    Args:
        workflow_id: ID do workflow
        user_id: ID do usuário
        
    Returns:
        Workflow encontrado ou None
    """
    workflow = await workflow_repository.get(workflow_id)
    if workflow and workflow.user_id == user_id:
        return workflow
    return None

async def update_workflow(workflow_id: UUID, workflow_data: WorkflowUpdate, user_id: UUID) -> Optional[Workflow]:
    """
    Atualiza um workflow existente.
    
    Args:
        workflow_id: ID do workflow
        workflow_data: Dados para atualização
        user_id: ID do usuário
        
    Returns:
        Workflow atualizado ou None
    """
    workflow = await get_workflow(workflow_id, user_id)
    if not workflow:
        return None
        
    for field, value in workflow_data.dict(exclude_unset=True).items():
        setattr(workflow, field, value)
        
    workflow.updated_at = datetime.utcnow()
    return await workflow_repository.update(workflow)

async def delete_workflow(workflow_id: UUID, user_id: UUID) -> bool:
    """
    Deleta um workflow.
    
    Args:
        workflow_id: ID do workflow
        user_id: ID do usuário
        
    Returns:
        True se o workflow foi deletado, False caso contrário
    """
    workflow = await get_workflow(workflow_id, user_id)
    if not workflow:
        return False
        
    await workflow_repository.delete(workflow_id)
    return True

async def list_workflows(user_id: UUID) -> List[Workflow]:
    """
    Lista todos os workflows de um usuário.
    
    Args:
        user_id: ID do usuário
        
    Returns:
        Lista de workflows
    """
    return await workflow_repository.list(f"SELECT * FROM c WHERE c.user_id = '{user_id}'")

async def execute_workflow(workflow_id: UUID, user_id: UUID) -> Optional[Workflow]:
    """
    Executa um workflow.
    
    Args:
        workflow_id: ID do workflow
        user_id: ID do usuário
        
    Returns:
        Workflow executado ou None
    """
    workflow = await get_workflow(workflow_id, user_id)
    if not workflow:
        return None
        
    workflow.status = WorkflowStatus.ACTIVE
    workflow.started_at = datetime.utcnow()
    workflow.updated_at = datetime.utcnow()
    
    try:
        for task in workflow.tasks:
            if task.status == TaskStatus.PENDING:
                await execute_task(task)
                
        workflow.status = WorkflowStatus.COMPLETED
        workflow.completed_at = datetime.utcnow()
    except Exception as e:
        workflow.status = WorkflowStatus.FAILED
        workflow.error_message = str(e)
        
    workflow.updated_at = datetime.utcnow()
    return await workflow_repository.update(workflow)

async def execute_task(task: Task) -> Task:
    """
    Executa uma tarefa individual.
    
    Args:
        task: Tarefa a ser executada
        
    Returns:
        Tarefa executada
    """
    task.status = TaskStatus.RUNNING
    task.started_at = datetime.utcnow()
    
    try:
        if task.type == TaskType.IA_MODULE:
            if task.parameters.get("type") == "chat":
                result = await execute_chat_task(task.parameters)
            elif task.parameters.get("type") == "document":
                result = await execute_document_processing_task(task.parameters)
            elif task.parameters.get("type") == "sentiment":
                result = await execute_sentiment_analysis_task(task.parameters)
            elif task.parameters.get("type") == "goal":
                result = await execute_goal_analysis_task(task.parameters)
            elif task.parameters.get("type") == "image":
                result = await execute_image_generation_task(task.parameters)
            else:
                raise ValueError(f"Tipo de módulo de IA inválido: {task.parameters.get('type')}")
        elif task.type == TaskType.DATA_PROCESSING:
            # TODO: Implementar processamento de dados
            result = {"success": True}
        elif task.type == TaskType.NOTIFICATION:
            # TODO: Implementar envio de notificação
            result = {"success": True}
        else:
            raise ValueError(f"Tipo de tarefa inválido: {task.type}")
            
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
    except Exception as e:
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        
    return task

async def verify_dependencies(task: Task) -> bool:
    """
    Verifica se todas as dependências de uma tarefa foram atendidas.
    
    Args:
        task: Tarefa a ser verificada
        
    Returns:
        True se todas as dependências foram atendidas, False caso contrário
    """
    if not task.dependencies:
        return True
        
    for dep_id in task.dependencies:
        dep_task = await workflow_repository.get_task(dep_id)
        if not dep_task or dep_task.status != TaskStatus.COMPLETED:
            return False
            
    return True

def get_workflow_status(workflow_id: UUID) -> Optional[WorkflowStatus]:
    workflow = get_workflow(workflow_id)
    return workflow.status if workflow else None

def update_workflow(workflow_id: UUID, workflow_update: WorkflowUpdate, user_id: str) -> Workflow:
    workflow = get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this workflow")
    
    update_data = workflow_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workflow, field, value)
    workflow.updated_at = datetime.utcnow()
    
    return workflow

def delete_workflow(workflow_id: UUID, user_id: str):
    workflow = get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this workflow")
    
    del workflows_db[workflow_id]
    # TODO: Deletar também todas as tasks associadas

def list_workflows(user_id: str) -> List[Workflow]:
    return [w for w in workflows_db.values() if w.user_id == user_id]

def create_task(workflow_id: UUID, task: TaskCreate, user_id: str) -> Task:
    workflow = get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to create tasks in this workflow")
    
    task_id = uuid4()
    new_task = Task(
        **task.dict(),
        task_id=task_id,
        workflow_id=workflow_id,
        status=TaskStatus.PENDING
    )
    tasks_db[task_id] = new_task
    return new_task

def list_tasks(workflow_id: UUID, user_id: str) -> List[Task]:
    workflow = get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view tasks in this workflow")
    
    return [t for t in tasks_db.values() if t.workflow_id == workflow_id]

def verify_dependencies(task: Task) -> bool:
    # TODO: Implementar verificação de dependências
    # Retorna True se todas as dependências foram atendidas
    return True 