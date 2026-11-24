
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# Roles disponibles
class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"


# Estados disponibles
class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLOCKED = "BLOCKED"


# Campos comunes del usuario
class UserBase(BaseModel):
    first_name: str = Field(min_length=2, max_length=80)
    last_name: Optional[str] = Field(default=None, max_length=120)
    email: str = Field(min_length=5, max_length=190)
    phone: Optional[str] = Field(default=None, max_length=25)
    avatar_url: Optional[str] = Field(default=None, max_length=500)


# Esquema para registrar un usuario
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


# Esquema para actualizar un usuario
class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=2, max_length=80)
    last_name: Optional[str] = Field(default=None, max_length=120)
    email: Optional[str] = Field(default=None, min_length=5, max_length=190)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    phone: Optional[str] = Field(default=None, max_length=25)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


# Esquema de respuesta
class UserResponse(UserBase):
    id: int
    role: UserRole
    status: UserStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Esquema para editar el perfil propio
class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=2, max_length=80)
    last_name: Optional[str] = Field(default=None, max_length=120)
    email: Optional[str] = Field(default=None, min_length=5, max_length=190)
    phone: Optional[str] = Field(default=None, max_length=25)
    avatar_url: Optional[str] = Field(default=None, max_length=500)


# Esquema para cambiar la contraseña
class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)
