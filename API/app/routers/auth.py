
from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

from app.routers.users import users
from app.core.security import verify_password, create_access_token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# 1. Inicio de sesión
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    # Normalizar el correo electrónico
    email = form_data.username.strip().lower()

    # Buscar usuario por correo
    user = next(
        (
            user for user in users.values()
            if user["email"].lower() == email
        ),
        None
    )

    # Comprobar que existe y que la contraseña es correcta
    if user is None or not verify_password(
        form_data.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Comprobar estado del usuario
    if user["status"] != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta no está activa"
        )

    # Crear token JWT
    access_token_expires = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "role": user["role"].value
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "role": user["role"],
            "status": user["status"]
        }
    }
