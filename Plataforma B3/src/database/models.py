from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class User(BaseModel):
    """
    Modelo de usuário.
    """
    id: UUID = Field(default_factory=uuid4)
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkflowStatus(str, Enum):
    """
    Status possíveis de um workflow.
    """
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

class Workflow(BaseModel):
    """
    Modelo de workflow.
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Theme(BaseModel):
    """
    Modelo de tema.
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Chat(BaseModel):
    """
    Modelo de chat.
    """
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    module_id: str
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentStatus(str, Enum):
    """
    Status possíveis de um documento.
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Document(BaseModel):
    """
    Modelo de documento.
    """
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    name: str
    content: str
    status: DocumentStatus = DocumentStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class GoalStatus(str, Enum):
    """
    Status possíveis de uma meta.
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Goal(BaseModel):
    """
    Modelo de meta.
    """
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    name: str
    description: Optional[str] = None
    status: GoalStatus = GoalStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    """
    Converte um modelo Pydantic para dicionário.
    
    Args:
        model: Modelo a ser convertido
        
    Returns:
        Dicionário com os dados do modelo
    """
    data = model.dict()
    data["id"] = str(data["id"])
    if "user_id" in data:
        data["user_id"] = str(data["user_id"])
    if "theme_id" in data:
        data["theme_id"] = str(data["theme_id"])
    if "target_date" in data:
        data["target_date"] = data["target_date"].isoformat()
    if "created_at" in data:
        data["created_at"] = data["created_at"].isoformat()
    if "updated_at" in data:
        data["updated_at"] = data["updated_at"].isoformat()
    return data

def dict_to_model(data: Dict[str, Any], model_class: type) -> BaseModel:
    """
    Converte um dicionário para modelo Pydantic.
    
    Args:
        data: Dicionário com os dados
        model_class: Classe do modelo
        
    Returns:
        Modelo Pydantic
    """
    if "id" in data:
        data["id"] = UUID(data["id"])
    if "user_id" in data:
        data["user_id"] = UUID(data["user_id"])
    if "theme_id" in data:
        data["theme_id"] = UUID(data["theme_id"])
    if "target_date" in data:
        data["target_date"] = datetime.fromisoformat(data["target_date"])
    if "created_at" in data:
        data["created_at"] = datetime.fromisoformat(data["created_at"])
    if "updated_at" in data:
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
    return model_class(**data) 