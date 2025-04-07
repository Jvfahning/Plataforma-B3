from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime
import asyncio
import logging
from ..workflows.models import Task, TaskStatus, TaskType
from ..ia_modules.models import TaskParameters, TaskResult
from ..ia_modules.services import execute_task as execute_ia_task
from .dag_manager import DAGManager

logger = logging.getLogger(__name__)

class TaskExecutor:
    def __init__(self, max_retries: int = 3, retry_delay: int = 5, max_parallel_tasks: int = 10):
        """
        Inicializa o executor de tarefas.
        
        Args:
            max_retries: Número máximo de tentativas
            retry_delay: Tempo de espera entre tentativas (em segundos)
            max_parallel_tasks: Número máximo de tarefas paralelas
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_parallel_tasks = max_parallel_tasks
        self.dag_manager = DAGManager()
        self.logger = logging.getLogger(__name__)
        self.running_tasks: Dict[UUID, asyncio.Task] = {}

    async def execute_workflow(self, workflow_id: UUID) -> Dict[str, TaskResult]:
        """
        Executa todas as tarefas de um workflow.
        
        Args:
            workflow_id: ID do workflow a ser executado
            
        Returns:
            Dicionário com os resultados de cada tarefa
        """
        tasks = self.dag_manager.get_workflow_tasks(workflow_id)
        if not tasks:
            raise ValueError(f"Workflow {workflow_id} não encontrado ou sem tarefas")
            
        parameters = {str(task.id): task.parameters for task in tasks}
        return await self.execute_tasks(tasks, parameters)

    async def execute_task(self, task: Task, parameters: TaskParameters) -> TaskResult:
        """
        Executa uma tarefa individual.
        
        Args:
            task: Tarefa a ser executada
            parameters: Parâmetros da tarefa
            
        Returns:
            Resultado da execução da tarefa
        """
        try:
            self.logger.info(f"Iniciando execução da tarefa {task.id}")
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            
            if task.type == TaskType.IA_MODULE:
                result = await execute_ia_task(parameters, task.user_id)
            else:
                # TODO: Implementar outros tipos de tarefa
                result = TaskResult(
                    success=True,
                    output="Tarefa executada com sucesso",
                    error=None
                )
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            self.logger.info(f"Tarefa {task.id} concluída com sucesso")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao executar tarefa {task.id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            
            return TaskResult(
                success=False,
                output=None,
                error=str(e)
            )

    async def execute_tasks(self, tasks: List[Task], parameters: Dict[str, TaskParameters]) -> Dict[str, TaskResult]:
        """
        Executa um conjunto de tarefas em paralelo, respeitando as dependências.
        
        Args:
            tasks: Lista de tarefas a serem executadas
            parameters: Dicionário de parâmetros para cada tarefa
            
        Returns:
            Dicionário com os resultados de cada tarefa
        """
        results = {}
        semaphore = asyncio.Semaphore(self.max_parallel_tasks)
        
        async def execute_with_retry(task: Task) -> TaskResult:
            for attempt in range(self.max_retries):
                try:
                    async with semaphore:
                        return await self.execute_task(task, parameters[str(task.id)])
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise
                    self.logger.warning(f"Tentativa {attempt + 1} falhou para tarefa {task.id}: {str(e)}")
                    await asyncio.sleep(self.retry_delay)
            
        execution_order = self.dag_manager.get_execution_order()
        
        for level in execution_order:
            tasks_in_level = [task for task in tasks if str(task.id) in level]
            if tasks_in_level:
                level_results = await asyncio.gather(
                    *[execute_with_retry(task) for task in tasks_in_level],
                    return_exceptions=True
                )
                
                for task, result in zip(tasks_in_level, level_results):
                    if isinstance(result, Exception):
                        self.logger.error(f"Erro ao executar tarefa {task.id}: {str(result)}")
                        results[str(task.id)] = TaskResult(
                            success=False,
                            output=None,
                            error=str(result)
                        )
                    else:
                        results[str(task.id)] = result
        
        return results

    async def cancel_task(self, workflow_id: UUID, task_id: UUID) -> None:
        """
        Cancela a execução de uma tarefa.
        
        Args:
            workflow_id: ID do workflow
            task_id: ID da tarefa
            
        Raises:
            ValueError: Se a tarefa não estiver em execução
        """
        if task_id not in self.running_tasks:
            raise ValueError("Tarefa não está em execução")
            
        task = self.running_tasks[task_id]
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
            
        await self.dag_manager.update_task_status(workflow_id, task_id, TaskStatus.FAILED)
        del self.running_tasks[task_id]

    async def get_task_status(self, workflow_id: UUID, task_id: UUID) -> TaskStatus:
        """
        Obtém o status de uma tarefa.
        
        Args:
            workflow_id: ID do workflow
            task_id: ID da tarefa
            
        Returns:
            Status da tarefa
            
        Raises:
            ValueError: Se a tarefa não existir
        """
        if workflow_id not in self.dag_manager.dags:
            raise ValueError("Workflow não encontrado")
            
        task = next((t for t in self.dag_manager.dags[workflow_id] if t.id == task_id), None)
        if not task:
            raise ValueError("Tarefa não encontrada")
            
        return task.status 