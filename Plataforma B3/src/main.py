from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from .workflows import router as workflows_router
from .ia_modules import router as ia_modules_router
from .orchestration import router as orchestration_router
from .database import close_connection
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

app = FastAPI(
    title="Plataforma B3",
    description="API para gerenciamento de workflows e módulos de IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de compressão
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middleware de segurança
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "*").split(",")
)

# Middleware de redirecionamento HTTPS
if os.getenv("ENFORCE_HTTPS", "false").lower() == "true":
    app.add_middleware(HTTPSRedirectMiddleware)

# Inclusão dos routers
app.include_router(workflows_router, prefix="/workflows", tags=["Workflows"])
app.include_router(ia_modules_router, prefix="/ia", tags=["IA Modules"])
app.include_router(orchestration_router, prefix="/orchestration", tags=["Orchestration"])

@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento executado ao encerrar a aplicação.
    Fecha a conexão com o banco de dados.
    """
    await close_connection()

@app.get("/health")
async def health_check():
    """
    Endpoint para verificação da saúde da aplicação.
    
    Returns:
        dict: Status da aplicação
    """
    return {
        "status": "healthy",
        "version": "1.0.0"
    } 