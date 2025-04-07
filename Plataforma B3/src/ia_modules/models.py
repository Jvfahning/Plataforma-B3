from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4

class IAModuleType(str, Enum):
    """
    Tipos de módulos de IA disponíveis.
    """
    CLOUD_IA = "cloud_ia"
    B3GPT = "b3gpt"
    EDUCATOR = "educator"
    SENTIMENT = "sentiment"
    GOAL_QA = "goal_qa"
    IMAGE_GENERATOR = "image_generator"
    PDF_PROCESSOR = "pdf_processor"

class IAModuleStatus(str, Enum):
    """
    Status possíveis de um módulo de IA.
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"

class IAModule(BaseModel):
    """
    Modelo de módulo de IA.
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    type: IAModuleType
    status: IAModuleStatus
    parameters_schema: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Theme(BaseModel):
    theme_id: UUID
    name: str
    description: str
    category: str
    created_at: datetime
    updated_at: datetime

class Document(BaseModel):
    document_id: UUID
    user_id: UUID
    filename: str
    file_type: str
    blob_url: str
    status: DocumentStatus
    embeddings: Optional[List[float]] = None
    processed_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class CloudIAParameters(BaseModel):
    """
    Parâmetros para o módulo CloudIA.
    """
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 1000

class B3GPTParameters(BaseModel):
    """
    Parâmetros para o módulo B3GPT.
    """
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 1000
    theme_id: UUID

class EducatorParameters(BaseModel):
    """
    Parâmetros para o módulo Educador Financeiro.
    """
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 1000
    theme_id: UUID

class SentimentParameters(BaseModel):
    """
    Parâmetros para o módulo de Análise de Sentimento.
    """
    text: str
    language: str = "pt"

class GoalQAParameters(BaseModel):
    """
    Parâmetros para o módulo de Análise de Metas.
    """
    question: str
    goal_id: UUID

class ImageGeneratorParameters(BaseModel):
    """
    Parâmetros para o módulo de Geração de Imagens.
    """
    prompt: str
    size: str = "1024x1024"
    quality: str = "standard"

class PDFProcessorParameters(BaseModel):
    """
    Parâmetros para o módulo de Processamento de PDF.
    """
    file_id: UUID
    extract_text: bool = True
    extract_tables: bool = False

class TaskParameters(BaseModel):
    """
    Parâmetros para uma tarefa de IA.
    """
    module_type: IAModuleType
    parameters: Dict[str, Any] = {}

class TaskResult(BaseModel):
    """
    Resultado de uma tarefa de IA.
    """
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float
    created_at: datetime = Field(default_factory=datetime.utcnow) 