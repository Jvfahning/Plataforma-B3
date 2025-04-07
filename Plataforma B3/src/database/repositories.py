from typing import List, Optional, Dict, Any, TypeVar, Generic, Type
from uuid import UUID
from .connection import get_container
from .models import (
    User, Workflow, Theme, Chat, Document, Goal,
    model_to_dict, dict_to_model
)

T = TypeVar("T")

# Queries SQL
QUERIES = {
    "user_by_username": "SELECT * FROM c WHERE c.username = @username",
    "user_by_email": "SELECT * FROM c WHERE c.email = @email",
    "workflow_by_user": "SELECT * FROM c WHERE c.user_id = @user_id",
    "theme_active": "SELECT * FROM c WHERE c.is_active = true",
    "chat_by_user": "SELECT * FROM c WHERE c.user_id = @user_id",
    "document_by_user": "SELECT * FROM c WHERE c.user_id = @user_id",
    "goal_by_user": "SELECT * FROM c WHERE c.user_id = @user_id"
}

class BaseRepository(Generic[T]):
    """
    Classe base para repositórios.
    """
    def __init__(self, container_name: str, model_class: Type[T]):
        self.container = get_container(container_name)
        self.model_class = model_class

    async def create(self, item: T) -> T:
        """
        Cria um novo item no container.
        
        Args:
            item: Item a ser criado
            
        Returns:
            Item criado
        """
        data = model_to_dict(item)
        result = await self.container.create_item(data)
        return dict_to_model(result, self.model_class)

    async def get(self, item_id: UUID) -> Optional[T]:
        """
        Obtém um item pelo ID.
        
        Args:
            item_id: ID do item
            
        Returns:
            Item encontrado ou None
        """
        try:
            result = await self.container.read_item(str(item_id), partition_key=str(item_id))
            return dict_to_model(result, self.model_class)
        except Exception:
            return None

    async def update(self, item: T) -> T:
        """
        Atualiza um item existente.
        
        Args:
            item: Item a ser atualizado
            
        Returns:
            Item atualizado
        """
        data = model_to_dict(item)
        result = await self.container.upsert_item(data)
        return dict_to_model(result, self.model_class)

    async def delete(self, item_id: UUID) -> None:
        """
        Deleta um item pelo ID.
        
        Args:
            item_id: ID do item
        """
        try:
            await self.container.delete_item(str(item_id), partition_key=str(item_id))
        except Exception:
            pass

    async def list(self, query: str = None, parameters: List[Dict[str, Any]] = None) -> List[T]:
        """
        Lista os itens do container.
        
        Args:
            query: Query SQL opcional
            parameters: Parâmetros da query opcional
            
        Returns:
            Lista de itens
        """
        if query:
            results = await self.container.query_items(
                query=query,
                parameters=parameters or [],
                enable_cross_partition_query=True
            )
        else:
            results = await self.container.read_all_items()
            
        return [dict_to_model(item, self.model_class) for item in results]

class UserRepository(BaseRepository[User]):
    """
    Repositório de usuários.
    """
    def __init__(self):
        super().__init__("users", User)

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Obtém um usuário pelo nome de usuário.
        
        Args:
            username: Nome de usuário
            
        Returns:
            Usuário encontrado ou None
        """
        results = await self.list(
            QUERIES["user_by_username"],
            [{"name": "@username", "value": username}]
        )
        return results[0] if results else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtém um usuário pelo email.
        
        Args:
            email: Email do usuário
            
        Returns:
            Usuário encontrado ou None
        """
        results = await self.list(
            QUERIES["user_by_email"],
            [{"name": "@email", "value": email}]
        )
        return results[0] if results else None

class WorkflowRepository(BaseRepository[Workflow]):
    """
    Repositório de workflows.
    """
    def __init__(self):
        super().__init__("workflows", Workflow)

    async def get_by_user(self, user_id: UUID) -> List[Workflow]:
        """
        Obtém os workflows de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de workflows
        """
        return await self.list(
            QUERIES["workflow_by_user"],
            [{"name": "@user_id", "value": str(user_id)}]
        )

class ThemeRepository(BaseRepository[Theme]):
    """
    Repositório de temas.
    """
    def __init__(self):
        super().__init__("themes", Theme)

    async def get_active(self) -> List[Theme]:
        """
        Obtém os temas ativos.
        
        Returns:
            Lista de temas
        """
        return await self.list(QUERIES["theme_active"])

class ChatRepository(BaseRepository[Chat]):
    """
    Repositório de chats.
    """
    def __init__(self):
        super().__init__("chats", Chat)

    async def get_by_user(self, user_id: UUID) -> List[Chat]:
        """
        Obtém os chats de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de chats
        """
        return await self.list(
            QUERIES["chat_by_user"],
            [{"name": "@user_id", "value": str(user_id)}]
        )

class DocumentRepository(BaseRepository[Document]):
    """
    Repositório de documentos.
    """
    def __init__(self):
        super().__init__("documents", Document)

    async def get_by_user(self, user_id: UUID) -> List[Document]:
        """
        Obtém os documentos de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de documentos
        """
        return await self.list(
            QUERIES["document_by_user"],
            [{"name": "@user_id", "value": str(user_id)}]
        )

class GoalRepository(BaseRepository[Goal]):
    """
    Repositório de metas.
    """
    def __init__(self):
        super().__init__("goals", Goal)

    async def get_by_user(self, user_id: UUID) -> List[Goal]:
        """
        Obtém as metas de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de metas
        """
        return await self.list(
            QUERIES["goal_by_user"],
            [{"name": "@user_id", "value": str(user_id)}]
        )

# Instâncias globais dos repositórios
user_repository = UserRepository()
workflow_repository = WorkflowRepository()
theme_repository = ThemeRepository()
chat_repository = ChatRepository()
document_repository = DocumentRepository()
goal_repository = GoalRepository() 