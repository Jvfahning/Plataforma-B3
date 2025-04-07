from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
from uuid import UUID
from .models import (
    IAModule, TaskParameters, TaskResult,
    CloudIAParameters, B3GPTParameters,
    EducatorParameters, SentimentParameters,
    GoalQAParameters, ImageGeneratorParameters,
    PDFProcessorParameters
)
from .services import (
    list_modules, get_module_details,
    execute_task, upload_file_to_blob,
    handle_file_processing, generate_image,
    process_pdf, extract_text_from_pdf
)
from ..auth.security import get_current_user
from ..database.models import User

router = APIRouter(prefix="/ia", tags=["ia"])

@router.get("/modules", response_model=List[IAModule])
async def get_modules(current_user: User = Depends(get_current_user)):
    """
    Lista os módulos de IA disponíveis.
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        Lista de módulos
    """
    return await list_modules()

@router.get("/modules/{module_id}", response_model=IAModule)
async def get_module(module_id: UUID, current_user: User = Depends(get_current_user)):
    """
    Obtém detalhes de um módulo de IA.
    
    Args:
        module_id: ID do módulo
        current_user: Usuário autenticado
        
    Returns:
        Detalhes do módulo
        
    Raises:
        HTTPException: Se o módulo não for encontrado
    """
    module = await get_module_details(module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Módulo não encontrado"
        )
    return module

@router.post("/execute", response_model=TaskResult)
async def execute_ia_task(
    parameters: TaskParameters,
    current_user: User = Depends(get_current_user)
):
    """
    Executa uma tarefa de IA.
    
    Args:
        parameters: Parâmetros da tarefa
        current_user: Usuário autenticado
        
    Returns:
        Resultado da tarefa
    """
    return await execute_task(parameters, current_user.id)

@router.post("/upload", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Faz upload de um arquivo.
    
    Args:
        file: Arquivo a ser enviado
        current_user: Usuário autenticado
        
    Returns:
        Informações do arquivo enviado
    """
    return await upload_file_to_blob(file, current_user.id)

@router.post("/process/{file_id}", response_model=TaskResult)
async def process_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Processa um arquivo enviado.
    
    Args:
        file_id: ID do arquivo
        current_user: Usuário autenticado
        
    Returns:
        Resultado do processamento
    """
    return await handle_file_processing(file_id, current_user.id)

@router.post("/generate-image", response_model=dict)
async def generate_ia_image(
    parameters: ImageGeneratorParameters,
    current_user: User = Depends(get_current_user)
):
    """
    Gera uma imagem a partir de um prompt.
    
    Args:
        parameters: Parâmetros da geração
        current_user: Usuário autenticado
        
    Returns:
        Informações da imagem gerada
    """
    return await generate_image(parameters)

@router.post("/process-pdf", response_model=dict)
async def process_pdf_file(
    parameters: PDFProcessorParameters,
    current_user: User = Depends(get_current_user)
):
    """
    Processa um arquivo PDF.
    
    Args:
        parameters: Parâmetros do processamento
        current_user: Usuário autenticado
        
    Returns:
        Resultado do processamento
    """
    return await process_pdf(parameters, current_user.id)

@router.post("/extract-text/{file_id}", response_model=TaskResult)
async def extract_pdf_text(
    file_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Extrai texto de um arquivo PDF.
    
    Args:
        file_id: ID do arquivo
        current_user: Usuário autenticado
        
    Returns:
        Texto extraído
    """
    return await extract_text_from_pdf(file_id, current_user.id) 