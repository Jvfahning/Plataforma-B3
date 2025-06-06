import os
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class Settings(BaseSettings):
    # Configurações do Azure OpenAI
    UFPB_OPENAI_API_KEY: str = Field(..., env="UFPB_OPENAI_API_KEY")
    UFPB_OPENAI_API_BASE: str = Field(..., env="UFPB_OPENAI_API_BASE")
    UFPB_OPENAI_API_VERSION: str = Field(..., env="UFPB_OPENAI_API_VERSION")
    UFPB_OPENAI_EMBEDDING_DEPLOYMENT: str = Field(..., env="UFPB_OPENAI_EMBEDDING_DEPLOYMENT")
    
    def MODEL_URL(self, model_name: str) -> str:
        return f"{self.UFPB_OPENAI_API_BASE}openai/deployments/{model_name}/chat/completions?api-version={self.UFPB_OPENAI_API_VERSION}"

    # Configurações do CosmosDB
    COSMOSDB_URL: str = Field(..., env="COSMOSDB_URL")
    COSMOSDB_KEY: str = Field(..., env="COSMOSDB_KEY")
    COSMOSDB_DB: str = Field(..., env="COSMOSDB_DB")
    COSMOSDB_CONTAINER: str = Field(..., env="COSMOSDB_CONTAINER")
    
    # Configurações da aplicação
    APP_NAME: str = Field(default="Plataforma B3 - IA", env="APP_NAME")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'

# Instancia as configurações para uso na aplicação
settings = Settings()