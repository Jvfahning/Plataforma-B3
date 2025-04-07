from typing import Dict, List, Optional, Set, Any
from uuid import UUID
from datetime import datetime
from ..workflows.models import Task, TaskStatus, TaskType
from ..database.repositories import workflow_repository
import networkx as nx
import graphviz
from pathlib import Path
import os

class DAGManager:
    def __init__(self):
        self.dags: Dict[UUID, List[Task]] = {}
        self.graph = nx.DiGraph()

    async def create_dag(self, workflow_id: UUID) -> None:
        """
        Cria um novo DAG a partir de um workflow.
        
        Args:
            workflow_id: ID do workflow
            
        Raises:
            ValueError: Se o workflow não existir
        """
        workflow = await workflow_repository.get(workflow_id)
        if not workflow:
            raise ValueError("Workflow não encontrado")
            
        if workflow_id in self.dags:
            raise ValueError("DAG já existe")
            
        self.dags[workflow_id] = workflow.tasks
        await self.validate_dag(workflow_id)

    async def validate_dag(self, workflow_id: UUID) -> None:
        """
        Valida se o DAG é válido (sem ciclos).
        
        Args:
            workflow_id: ID do workflow
            
        Raises:
            ValueError: Se o DAG contiver ciclos
        """
        if workflow_id not in self.dags:
            raise ValueError("DAG não encontrado")
            
        tasks = self.dags[workflow_id]
        visited: Set[UUID] = set()
        recursion_stack: Set[UUID] = set()
        
        for task in tasks:
            if task.id not in visited:
                if await self._has_cycle(task, visited, recursion_stack):
                    raise ValueError("DAG contém ciclos")

    async def _has_cycle(self, task: Task, visited: Set[UUID], recursion_stack: Set[UUID]) -> bool:
        """
        Verifica se existe um ciclo a partir de uma tarefa.
        
        Args:
            task: Tarefa inicial
            visited: Conjunto de tarefas visitadas
            recursion_stack: Conjunto de tarefas na pilha de recursão
            
        Returns:
            True se existir ciclo, False caso contrário
        """
        visited.add(task.id)
        recursion_stack.add(task.id)
        
        for dependency in task.dependencies:
            if dependency not in visited:
                if await self._has_cycle(self._get_task_by_id(dependency), visited, recursion_stack):
                    return True
            elif dependency in recursion_stack:
                return True
                
        recursion_stack.remove(task.id)
        return False

    def _get_task_by_id(self, task_id: UUID) -> Optional[Task]:
        """
        Obtém uma tarefa pelo ID em todos os DAGs.
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            Tarefa encontrada ou None
        """
        for tasks in self.dags.values():
            for task in tasks:
                if task.id == task_id:
                    return task
        return None

    async def add_task(self, workflow_id: UUID, task: Task) -> None:
        """
        Adiciona uma nova tarefa ao DAG.
        
        Args:
            workflow_id: ID do workflow
            task: Tarefa a ser adicionada
            
        Raises:
            ValueError: Se o DAG não existir
        """
        if workflow_id not in self.dags:
            raise ValueError("DAG não encontrado")
            
        self.dags[workflow_id].append(task)
        await self.validate_dag(workflow_id)

    async def remove_task(self, workflow_id: UUID, task_id: UUID) -> None:
        """
        Remove uma tarefa do DAG.
        
        Args:
            workflow_id: ID do workflow
            task_id: ID da tarefa
            
        Raises:
            ValueError: Se o DAG ou a tarefa não existirem
        """
        if workflow_id not in self.dags:
            raise ValueError("DAG não encontrado")
            
        tasks = self.dags[workflow_id]
        task = next((t for t in tasks if t.id == task_id), None)
        if not task:
            raise ValueError("Tarefa não encontrada")
            
        # Remove a tarefa e suas dependências
        tasks.remove(task)
        for t in tasks:
            if task_id in t.dependencies:
                t.dependencies.remove(task_id)
                
        await self.validate_dag(workflow_id)

    async def update_task_status(self, workflow_id: UUID, task_id: UUID, status: TaskStatus) -> None:
        """
        Atualiza o status de uma tarefa.
        
        Args:
            workflow_id: ID do workflow
            task_id: ID da tarefa
            status: Novo status
            
        Raises:
            ValueError: Se o DAG ou a tarefa não existirem
        """
        if workflow_id not in self.dags:
            raise ValueError("DAG não encontrado")
            
        task = next((t for t in self.dags[workflow_id] if t.id == task_id), None)
        if not task:
            raise ValueError("Tarefa não encontrada")
            
        task.status = status
        task.updated_at = datetime.utcnow()

    def get_task_dependencies(self, workflow_id: UUID, task_id: UUID) -> List[UUID]:
        """
        Obtém as dependências de uma tarefa.
        
        Args:
            workflow_id: ID do workflow
            task_id: ID da tarefa
            
        Returns:
            Lista de IDs das dependências
            
        Raises:
            ValueError: Se o DAG ou a tarefa não existirem
        """
        if workflow_id not in self.dags:
            raise ValueError("DAG não encontrado")
            
        task = next((t for t in self.dags[workflow_id] if t.id == task_id), None)
        if not task:
            raise ValueError("Tarefa não encontrada")
            
        return task.dependencies

    def get_dependent_tasks(self, workflow_id: UUID, task_id: UUID) -> List[UUID]:
        """
        Obtém as tarefas que dependem de uma tarefa específica.
        
        Args:
            workflow_id: ID do workflow
            task_id: ID da tarefa
            
        Returns:
            Lista de IDs das tarefas dependentes
            
        Raises:
            ValueError: Se o DAG não existir
        """
        if workflow_id not in self.dags:
            raise ValueError("DAG não encontrado")
            
        dependent_tasks = []
        for task in self.dags[workflow_id]:
            if task_id in task.dependencies:
                dependent_tasks.append(task.id)
                
        return dependent_tasks

    def add_task_to_graph(self, task_id: UUID, dependencies: List[UUID] = None) -> None:
        """
        Adiciona uma tarefa ao DAG.
        
        Args:
            task_id: ID da tarefa
            dependencies: Lista de IDs das tarefas que devem ser executadas antes
        """
        self.graph.add_node(str(task_id))
        if dependencies:
            for dep in dependencies:
                self.graph.add_edge(str(dep), str(task_id))

    def remove_task_from_graph(self, task_id: UUID) -> None:
        """
        Remove uma tarefa do DAG.
        
        Args:
            task_id: ID da tarefa a ser removida
        """
        self.graph.remove_node(str(task_id))

    def get_task_dependencies_from_graph(self, task_id: UUID) -> List[UUID]:
        """
        Retorna as dependências de uma tarefa.
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            Lista de IDs das tarefas dependentes
        """
        return [UUID(dep) for dep in self.graph.predecessors(str(task_id))]

    def get_task_dependents_from_graph(self, task_id: UUID) -> List[UUID]:
        """
        Retorna as tarefas que dependem da tarefa especificada.
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            Lista de IDs das tarefas dependentes
        """
        return [UUID(dep) for dep in self.graph.successors(str(task_id))]

    def is_valid_graph(self) -> bool:
        """
        Verifica se o grafo é um DAG válido.
        
        Returns:
            True se for válido, False caso contrário
        """
        try:
            return nx.is_directed_acyclic_graph(self.graph)
        except:
            return False

    def get_execution_order(self) -> List[List[UUID]]:
        """
        Retorna a ordem de execução das tarefas.
        
        Returns:
            Lista de listas de IDs de tarefas, onde cada lista representa um nível de execução
        """
        try:
            levels = list(nx.topological_generations(self.graph))
            return [[UUID(task_id) for task_id in level] for level in levels]
        except:
            return []

    def visualize_graph(self, output_path: str, format: str = "png") -> str:
        """
        Gera uma visualização do grafo.
        
        Args:
            output_path: Caminho onde o arquivo será salvo
            format: Formato do arquivo (png, svg, pdf)
            
        Returns:
            Caminho do arquivo gerado
        """
        dot = graphviz.Digraph()
        
        for node in self.graph.nodes():
            dot.node(str(node))
            
        for edge in self.graph.edges():
            dot.edge(str(edge[0]), str(edge[1]))
            
        file_path = f"{output_path}.{format}"
        dot.render(output_path, format=format, cleanup=True)
        
        return file_path

    def to_dict_graph(self) -> Dict[str, Any]:
        """
        Converte o grafo para um dicionário.
        
        Returns:
            Dicionário representando o grafo
        """
        return {
            "nodes": list(self.graph.nodes()),
            "edges": list(self.graph.edges())
        }

    @classmethod
    def from_dict_graph(cls, data: Dict[str, Any]) -> 'DAGManager':
        """
        Cria um DAGManager a partir de um dicionário.
        
        Args:
            data: Dicionário representando o grafo
            
        Returns:
            Nova instância de DAGManager
        """
        manager = cls()
        for node in data["nodes"]:
            manager.graph.add_node(node)
        for edge in data["edges"]:
            manager.graph.add_edge(edge[0], edge[1])
        return manager

    def get_workflow_tasks(self, workflow_id: UUID) -> List[Task]:
        """
        Obtém as tarefas de um workflow.
        
        Args:
            workflow_id: ID do workflow
            
        Returns:
            Lista de tarefas
            
        Raises:
            ValueError: Se o workflow não existir
        """
        if workflow_id not in self.dags:
            raise ValueError("Workflow não encontrado")
            
        return self.dags[workflow_id] 