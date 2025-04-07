from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional

class UserCreate(BaseModel):
    """
    Modelo para criação de usuário.
    """
    username: str
    email: EmailStr
    password: str

class User(BaseModel):
    """
    Modelo de usuário.
    """
    id: UUID
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class Token(BaseModel):
    """
    Modelo de token JWT.
    """
    id: UUID
    user_id: UUID
    token: str
    issued_at: datetime
    expires_at: datetime
    revoked: bool = False 