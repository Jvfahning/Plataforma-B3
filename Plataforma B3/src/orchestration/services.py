from typing import Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
import logging
from ..workflows.models import Task, TaskStatus, TaskType
from ..ia_modules.models import TaskParameters, TaskResult
from .dag_manager import DAGManager
from .executor import TaskExecutor

logger = logging.getLogger(__name__)

class OrchestrationService:
    def __init__(self):
        """Inicializa o serviço de orquestração."""
        self.dag_manager = DAGManager()
        self.executor = TaskExecutor()
        self.logger = logging.getLogger(__name__)

    async def create_workflow(self, tasks: List[Task], user_id: UUID) -> UUID:
        """
        Cria um novo workflow.
        
        Args:
            tasks: Lista de tarefas do workflow
            user_id: ID do usuário criador
            
        Returns:
            ID do workflow criado
            
        Raises:
            ValueError: Se o workflow for inválido
        """
        workflow_id = uuid4()
        
        # Adiciona o user_id a todas as tarefas
        for task in tasks:
            task.user_id = user_id
            
        if not self.dag_manager.is_valid_graph(tasks):
            raise ValueError("Workflow contém ciclos")
            
        self.dag_manager.create_dag(workflow_id, tasks)
        return workflow_id

    async def get_workflow_tasks(self, workflow_id: UUID) -> List[Task]:
        """
        Obtém as tarefas de um workflow.
        
        Args:
            workflow_id: ID do workflow
            
        Returns:
            Lista de tarefas do workflow
            
        Raises:
            ValueError: Se o workflow não existir
        """
        if workflow_id not in self.dag_manager.dags:
            raise ValueError("Workflow não encontrado")
            
        return self.dag_manager.dags[workflow_id]

    async def update_workflow(self, workflow_id: UUID, tasks: List[Task]) -> None:
        """
        Atualiza as tarefas de um workflow.
        
        Args:
            workflow_id: ID do workflow
            tasks: Nova lista de tarefas
            
        Raises:
            ValueError: Se o workflow for inválido
        """
        if not self.dag_manager.is_valid_graph(tasks):
            raise ValueError("Workflow contém ciclos")
            
        self.dag_manager.update_dag(workflow_id, tasks)

    async def delete_workflow(self, workflow_id: UUID) -> None:
        """
        Remove um workflow.
        
        Args:
            workflow_id: ID do workflow a ser removido
        """
        self.dag_manager.delete_dag(workflow_id)

    async def execute_workflow(self, workflow_id: UUID) -> Dict[str, TaskResult]:
        """
        Executa um workflow.
        
        Args:
            workflow_id: ID do workflow
            
        Returns:
            Dicionário com os resultados de cada tarefa
            
        Raises:
            ValueError: Se o workflow não existir
        """
        if workflow_id not in self.dag_manager.dags:
            raise ValueError("Workflow não encontrado")
            
        return await self.executor.execute_workflow(workflow_id)

    async def visualize_workflow(self, workflow_id: UUID) -> str:
        """
        Gera uma visualização do workflow.
        
        Args:
            workflow_id: ID do workflow
            
        Returns:
            String com a visualização em formato DOT
            
        Raises:
            ValueError: Se o workflow não existir
        """
        if workflow_id not in self.dag_manager.dags:
            raise ValueError("Workflow não encontrado")
            
        return self.dag_manager.visualize_graph(workflow_id)

    async def get_workflow_status(self, workflow_id: UUID) -> Dict[str, int]:
        """
        Obtém o status atual do workflow.
        
        Args:
            workflow_id: ID do workflow
            
        Returns:
            Dicionário com contagem de tarefas por status
            
        Raises:
            ValueError: Se o workflow não existir
        """
        if workflow_id not in self.dag_manager.dags:
            raise ValueError("Workflow não encontrado")
            
        tasks = self.dag_manager.dags[workflow_id]
        status_counts = {
            "completed": 0,
            "failed": 0,
            "running": 0,
            "pending": 0
        }
        
        for task in tasks:
            status_counts[task.status.value] += 1
            
        return status_counts

    async def get_execution_history(self, workflow_id: UUID) -> List[Dict]:
        """
        Obtém o histórico de execução de um workflow.
        
        Args:
            workflow_id: ID do workflow
            
        Returns:
            Lista de registros de execução
            
        Raises:
            ValueError: Se o workflow não existir
        """
        if workflow_id not in self.dag_manager.dags:
            raise ValueError("Workflow não encontrado")
            
        tasks = self.dag_manager.dags[workflow_id]
        history = []
        
        for task in tasks:
            history.append({
                "task_id": str(task.id),
                "status": task.status.value,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            })
            
        return history

    async def cleanup_workflow_execution(self, workflow_id: UUID) -> None:
        """
        Limpa os recursos de execução de um workflow.
        
        Args:
            workflow_id: ID do workflow
        """
        if workflow_id in self.dag_manager.dags:
            tasks = self.dag_manager.dags[workflow_id]
            for task in tasks:
                if task.id in self.executor.running_tasks:
                    await self.executor.cancel_task(workflow_id, task.id) 