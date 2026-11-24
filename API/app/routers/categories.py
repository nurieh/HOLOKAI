
from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)

from app.core.dependencies import get_current_admin

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

# DATOS TEMPORALES PARA REALIZAR PRUEBAS
categories = {
    1: {
        "id": 1,
        "name": "Pokémon",
        "description": "Productos y cartas de Pokémon",
        "is_active": True
    },
    2: {
        "id": 2,
        "name": "Yu-Gi-Oh!",
        "description": "Productos y cartas de Yu-Gi-Oh!",
        "is_active": True
    },
    3: {
        "id": 3,
        "name": "Magic: The Gathering",
        "description": "Productos y cartas de Magic",
        "is_active": True
    },
    4: {
        "id": 4,
        "name": "Dragon Ball",
        "description": "Productos y cartas de Dragon Ball",
        "is_active": True
    }
}

next_id = 4


# GET: Listar todas las categorías
@router.get("/", response_model=list[CategoryResponse])
def get_categories():
    return [
        category for category in categories.values()
        if category["is_active"]
    ]


# GET: Consultar una categoría
@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int):

    category = categories.get(category_id)

    if not category or not category["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    return category


# POST: Crear una categoría
@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_category(
    category: CategoryCreate,
    current_admin: dict = Depends(get_current_admin)
):

    global next_id

    # Comprobar que no exista otra categoría con el mismo nombre
    for existing_category in categories.values():
        if (
            existing_category["name"].lower() == category.name.lower()
            and existing_category["is_active"]
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una categoría con ese nombre"
            )

    new_category = {
        "id": next_id,
        **category.model_dump(),
        "is_active": True
    }

    categories[next_id] = new_category
    next_id += 1

    return new_category


# PUT: Modificar una categoría
@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    current_admin: dict = Depends(get_current_admin)
):

    existing_category = categories.get(category_id)

    if not existing_category or not existing_category["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    updated_data = category.model_dump(exclude_unset=True)

    if "name" in updated_data:
        for other_id, other_category in categories.items():
            if (
                other_id != category_id
                and other_category["is_active"]
                and other_category["name"].lower()
                == updated_data["name"].lower()
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe otra categoría con ese nombre"
                )

    existing_category.update(updated_data)

    return existing_category


# DELETE: Desactivar una categoría
@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    current_admin: dict = Depends(get_current_admin)
):

    category = categories.get(category_id)

    if not category or not category["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    category["is_active"] = False

    return {
        "message": "Categoría desactivada correctamente"
    }
