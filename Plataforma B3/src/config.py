from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field, HttpUrl

class Settings(BaseSettings):
    # Configurações da API
    API_KEY: str = Field(..., min_length=1)
    MODEL_URL: HttpUrl = Field(default="https://b3gpt.intraservice.azr/internal-api/b3gpt-llms/v1/openai/deployments/gpt4o/chat/completions")
    
    # Configurações do MongoDB
    MONGODB_URL: str = Field(default="mongodb://localhost:27017")
    MONGODB_DB: str = Field(default="plataforma_b3", min_length=1)
    MONGODB_COLLECTION: str = Field(default="flows", min_length=1)
    
    # Configurações da aplicação
    APP_NAME: str = Field(default="Plataforma B3 - IA", min_length=1)
    DEBUG: bool = Field(default=False)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'

settings = Settings() 