import os
from typing import Optional
from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class Settings(BaseSettings):
    # Configurações do Azure OpenAI
    UFPB_OPENAI_API_KEY: str = Field(..., env="UFPB_OPENAI_API_KEY")
    UFPB_OPENAI_API_BASE: str = Field(..., env="UFPB_OPENAI_API_BASE")
    UFPB_LLM_DEPLOYMENT_NAME_4O: str = Field(..., env="UFPB_LLM_DEPLOYMENT_NAME_4O")
    UFPB_OPENAI_API_VERSION: str = Field(..., env="UFPB_OPENAI_API_VERSION")
    
    # URL do endpoint do modelo
    @property
    def MODEL_URL(self) -> str:
        """Retorna a URL completa do endpoint"""
        return f"{self.UFPB_OPENAI_API_BASE}openai/deployments/{self.UFPB_LLM_DEPLOYMENT_NAME_4O}/chat/completions?api-version={self.UFPB_OPENAI_API_VERSION}"
    
    # Configurações do MongoDB
    MONGODB_URL: str = Field(default="mongodb://localhost:27017", env="MONGODB_URL")
    MONGODB_DB: str = Field(default="plataforma_b3", env="MONGODB_DB")
    MONGODB_COLLECTION: str = Field(default="flows", env="MONGODB_COLLECTION")
    
    # Configurações da aplicação
    APP_NAME: str = Field(default="Plataforma B3 - IA", env="APP_NAME")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'

settings = Settings() 