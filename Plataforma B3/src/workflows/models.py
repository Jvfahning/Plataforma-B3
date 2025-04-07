from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskType(str, Enum):
    IA_MODULE = "ia_module"
    DATA_PROCESSING = "data_processing"
    NOTIFICATION = "notification"

class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    type: TaskType
    status: TaskStatus = TaskStatus.PENDING
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[UUID] = Field(default_factory=list)
    user_id: UUID
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Workflow(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.DRAFT
    tasks: List[Task] = Field(default_factory=list)
    user_id: UUID
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tasks: List[Task] = Field(default_factory=list)

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tasks: Optional[List[Task]] = None
    status: Optional[WorkflowStatus] = None 