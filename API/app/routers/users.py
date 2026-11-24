
from datetime import datetime
from fastapi import APIRouter, HTTPException, Path, Query, status, Depends
from pwdlib import PasswordHash

from app.core.dependencies import get_current_admin

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserRole,
    UserStatus
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

password_hash = PasswordHash.recommended()

# Generar hash de contraseña
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# Comprobar si el email ya existe
def check_email(email: str, exclude_id: int = None):
    normalized_email = email.strip().lower()

    for user in users.values():
        if (
            user["email"].lower() == normalized_email
            and user["id"] != exclude_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese email"
            )


# Obtener usuario por ID
def get_existing_user(user_id: int):
    user = users.get(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return user

# Almacenamiento temporal de usuarios
users = {
    1: {
        "id": 1,
        "first_name": "Administrador",
        "last_name": "HOLOKAI",
        "email": "admin@holokai.com",
        "password_hash": hash_password("Admin12345"),
        "phone": "600000001",
        "avatar_url": None,
        "role": UserRole.ADMIN,
        "status": UserStatus.ACTIVE,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    2: {
        "id": 2,
        "first_name": "Cliente",
        "last_name": "Prueba",
        "email": "cliente@holokai.com",
        "password_hash": hash_password("Cliente12345"),
        "phone": "600000002",
        "avatar_url": None,
        "role": UserRole.CUSTOMER,
        "status": UserStatus.ACTIVE,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
}

next_id = 3

# Listar usuarios
@router.get("/", response_model=list[UserResponse])
def get_users(
    search: str = Query(default=None),
    role: UserRole = Query(default=None),
    user_status: UserStatus = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_admin: dict = Depends(get_current_admin)
):
    result = list(users.values())

    if search:
        search = search.lower()

        result = [
            user for user in result
            if search in user["first_name"].lower()
            or search in (user["last_name"] or "").lower()
            or search in user["email"].lower()
        ]

    if role:
        result = [user for user in result if user["role"] == role]

    if user_status:
        result = [
            user for user in result
            if user["status"] == user_status
        ]

    start = (page - 1) * limit

    return result[start:start + limit]


# Consultar usuario por ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
        user_id: int = Path(gt=0),
        current_admin: dict = Depends(get_current_admin)
):
    return get_existing_user(user_id)


# Registrar usuario
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(user_data: UserCreate):
    global next_id

    email = user_data.email.strip().lower()
    check_email(email)

    now = datetime.now()

    new_user = {
        "id": next_id,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "email": email,
        "password_hash": hash_password(user_data.password),
        "phone": user_data.phone,
        "avatar_url": user_data.avatar_url,
        "role": UserRole.CUSTOMER,
        "status": UserStatus.ACTIVE,
        "created_at": now,
        "updated_at": now
    }

    users[next_id] = new_user
    next_id += 1

    return new_user


# Actualizar usuario
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_data: UserUpdate,
    user_id: int = Path(gt=0),
    current_admin: dict = Depends(get_current_admin)
):
    user = get_existing_user(user_id)

    update_data = user_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se han enviado campos para actualizar"
        )

    for field, value in update_data.items():
        if value is None and field not in ("last_name", "phone", "avatar_url"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El campo '{field}' no puede ser null"
            )

    if "email" in update_data:
        email = update_data["email"].strip().lower()
        check_email(email, exclude_id=user_id)
        update_data["email"] = email

    if "password" in update_data:
        update_data["password_hash"] = hash_password(
            update_data.pop("password")
        )

    user.update(update_data)
    user["updated_at"] = datetime.now()

    return user


# 5. Desactivar usuario
@router.delete("/{user_id}")
def delete_user(
        user_id: int = Path(gt=0),
        current_admin: dict = Depends(get_current_admin)
):
    user = get_existing_user(user_id)

    if user["status"] == UserStatus.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está desactivado"
        )

    user["status"] = UserStatus.INACTIVE
    user["updated_at"] = datetime.now()

    return {
        "message": "Usuario desactivado correctamente",
        "user_id": user_id
    }
