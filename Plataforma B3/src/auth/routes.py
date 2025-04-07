from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from typing import Optional
from ..database import user_repository
from .models import UserCreate, User, Token
from .security import (
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["autenticação"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Autentica um usuário com base no nome de usuário e senha.
    """
    user = await user_repository.get_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint para login de usuário.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return Token(
        id=user.id,
        user_id=user.id,
        token=access_token,
        issued_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + access_token_expires,
        revoked=False
    )

@router.post("/register", response_model=User)
async def register(user_data: UserCreate):
    """
    Endpoint para registro de novo usuário.
    """
    existing_user = await user_repository.get_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já existe"
        )
    
    existing_email = await user_repository.get_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está em uso"
        )
    
    user = await user_repository.create(user_data)
    return user

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Endpoint para obter informações do usuário atual.
    """
    return current_user 