
from datetime import datetime
from fastapi import APIRouter, HTTPException, Path, status

from app.schemas.product_image import (
    ProductImageCreate,
    ProductImageUpdate,
    ProductImageResponse
)

from app.routers.products import products as product_store


router = APIRouter(
    prefix="/products/{product_id}/images",
    tags=["Product Images"]
)


# Almacenamiento temporal de imágenes
product_images = {
    1: {
        "id": 1,
        "product_id": 1,
        "image_url": "https://example.com/pokemon-booster.jpg",
        "is_main": True,
        "position": 0,
        "created_at": datetime.now()
    },
    2: {
        "id": 2,
        "product_id": 1,
        "image_url": "https://example.com/pokemon-booster-back.jpg",
        "is_main": False,
        "position": 1,
        "created_at": datetime.now()
    },
    3: {
        "id": 3,
        "product_id": 2,
        "image_url": "https://example.com/yugioh-booster.jpg",
        "is_main": True,
        "position": 0,
        "created_at": datetime.now()
    }
}

next_id = 4


# Comprobar que existe el producto
def check_product(product_id: int):
    if product_id not in product_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El producto no existe"
        )


# Obtener una imagen y comprobar que pertenece al producto
def get_product_image(product_id: int, image_id: int):
    check_product(product_id)

    image = product_images.get(image_id)

    if image is None or image["product_id"] != product_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La imagen no existe para este producto"
        )

    return image


# Quitar el estado principal a las demás imágenes del producto
def unset_main_images(product_id: int, exclude_id: int = None):
    for image in product_images.values():
        if (
            image["product_id"] == product_id
            and image["id"] != exclude_id
        ):
            image["is_main"] = False


# 1. Listar imágenes de un producto
@router.get(
    "/",
    response_model=list[ProductImageResponse]
)
def get_product_images(
    product_id: int = Path(gt=0)
):
    check_product(product_id)

    images = [
        image
        for image in product_images.values()
        if image["product_id"] == product_id
    ]

    return sorted(
        images,
        key=lambda image: (image["position"], image["id"])
    )


# 2. Consultar una imagen concreta
@router.get(
    "/{image_id}",
    response_model=ProductImageResponse
)
def get_product_image_by_id(
    product_id: int = Path(gt=0),
    image_id: int = Path(gt=0)
):
    return get_product_image(product_id, image_id)


# 3. Añadir una imagen
@router.post(
    "/",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product_image(
    image_data: ProductImageCreate,
    product_id: int = Path(gt=0)
):
    global next_id

    check_product(product_id)

    if image_data.is_main:
        unset_main_images(product_id)

    new_image = {
        "id": next_id,
        "product_id": product_id,
        **image_data.model_dump(),
        "created_at": datetime.now()
    }

    product_images[next_id] = new_image
    next_id += 1

    return new_image


# 4. Actualizar una imagen
@router.put(
    "/{image_id}",
    response_model=ProductImageResponse
)
def update_product_image(
    image_data: ProductImageUpdate,
    product_id: int = Path(gt=0),
    image_id: int = Path(gt=0)
):
    image = get_product_image(product_id, image_id)

    update_data = image_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se han enviado campos para actualizar"
        )

    for field in ("image_url", "position", "is_main"):
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El campo '{field}' no puede ser null"
            )

    if update_data.get("is_main") is True:
        unset_main_images(product_id, exclude_id=image_id)

    image.update(update_data)

    return image


# 5. Eliminar una imagen
@router.delete("/{image_id}")
def delete_product_image(
    product_id: int = Path(gt=0),
    image_id: int = Path(gt=0)
):
    image = get_product_image(product_id, image_id)

    del product_images[image_id]

    return {
        "message": "Imagen eliminada correctamente",
        "product_id": product_id,
        "image_id": image_id
    }
