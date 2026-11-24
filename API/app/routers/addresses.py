from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.address import (
    AddressCreate,
    AddressUpdate,
    AddressResponse
)
from app.schemas.user import UserRole
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"]
)


# ==========================================
# ALMACENAMIENTO TEMPORAL EN MEMORIA
# ==========================================

addresses = {}
next_address_id = 1


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def get_existing_address(address_id: int):
    address = addresses.get(address_id)

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dirección no encontrada"
        )

    return address


def check_address_owner(address, user):
    if (
        user["role"] != UserRole.ADMIN
        and address["user_id"] != user["id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para gestionar esta dirección"
        )

    return address


def set_default_address(user_id: int, address_id: int):
    """
    Marca una dirección como predeterminada
    y desmarca las demás direcciones del usuario.
    """
    for address in addresses.values():
        if address["user_id"] == user_id:
            address["is_default"] = (
                address["id"] == address_id
            )


# ==========================================
# GET - LISTAR DIRECCIONES
# ==========================================

@router.get("/", response_model=list[AddressResponse])
def get_addresses(
    is_default: bool | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    result = list(addresses.values())

    # Los clientes solo consultan sus direcciones
    if current_user["role"] != UserRole.ADMIN:
        result = [
            address for address in result
            if address["user_id"] == current_user["id"]
        ]

    if is_default is not None:
        result = [
            address for address in result
            if address["is_default"] == is_default
        ]

    result.sort(key=lambda address: address["id"])

    return result[skip:skip + limit]


# ==========================================
# GET - CONSULTAR DIRECCIÓN POR ID
# ==========================================

@router.get("/{address_id}", response_model=AddressResponse)
def get_address(
    address_id: int,
    current_user: dict = Depends(get_current_user)
):
    address = get_existing_address(address_id)

    check_address_owner(address, current_user)

    return address


# ==========================================
# POST - CREAR DIRECCIÓN
# ==========================================

@router.post(
    "/",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED
)
def create_address(
    address_data: AddressCreate,
    current_user: dict = Depends(get_current_user)
):
    global next_address_id

    address = {
        "id": next_address_id,
        "user_id": current_user["id"],
        "recipient_name": address_data.recipient_name,
        "phone": address_data.phone,
        "street": address_data.street,
        "city": address_data.city,
        "postal_code": address_data.postal_code,
        "province": address_data.province,
        "country": address_data.country,
        "is_default": False,
        "created_at": datetime.now()
    }

    addresses[next_address_id] = address

    # Si se solicita como predeterminada,
    # se desmarcan las anteriores del usuario.
    if address_data.is_default:
        set_default_address(
            current_user["id"],
            next_address_id
        )

    next_address_id += 1

    return address


# ==========================================
# PUT - ACTUALIZAR DIRECCIÓN
# ==========================================

@router.put("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    address_data: AddressUpdate,
    current_user: dict = Depends(get_current_user)
):
    address = get_existing_address(address_id)

    check_address_owner(address, current_user)

    update_data = address_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field != "is_default":
            address[field] = value

    if update_data.get("is_default") is True:
        set_default_address(
            address["user_id"],
            address_id
        )
    elif update_data.get("is_default") is False:
        address["is_default"] = False

    return address


# ==========================================
# DELETE - ELIMINAR DIRECCIÓN
# ==========================================

@router.delete("/{address_id}")
def delete_address(
    address_id: int,
    current_user: dict = Depends(get_current_user)
):
    address = get_existing_address(address_id)

    check_address_owner(address, current_user)

    del addresses[address_id]

    return {
        "message": "Dirección eliminada correctamente",
        "address_id": address_id
    }