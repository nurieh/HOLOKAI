
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductStatus
)

# Importamos temporalmente las categorías
from app.routers.categories import categories as category_store


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# ==========================================
# ALMACENAMIENTO TEMPORAL DE PRODUCTOS
# ==========================================

products = {
    1: {
        "id": 1,
        "category_id": 1,
        "name": "Pokemon: 151 Scarlet & Violet Ultra Premium Collection",
        "sku": "POK-151",
        "description": "Caja de colección Ultra Premium de la expansión 151 Scarlet & Violet de Pokemon TCG",
        "price": Decimal("5.99"),
        "stock": 25,
        "status": ProductStatus.ACTIVE,
        "is_featured": True,
        "is_new": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    2: {
        "id": 2,
        "category_id": 4,
        "name": "Dragon Ball Super: Fusion World -Ultra Limit- Booster Box",
        "sku": "DBS-001",
        "description": "Lote de sobres de la expansión Fusion World -Ultra Limit- de Dragon Ball Super TCG",
        "price": Decimal("4.99"),
        "stock": 30,
        "status": ProductStatus.ACTIVE,
        "is_featured": False,
        "is_new": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
}

next_id = 3


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def check_category(category_id: int):
    """
    Comprueba que la categoría exista y esté activa.
    """

    category = category_store.get(category_id)

    if not category or not category["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La categoría indicada no existe o está inactiva"
        )


def check_sku(sku: str, exclude_id: int = None):
    """
    Comprueba que el SKU no esté utilizado
    por otro producto activo o inactivo.
    """

    for product_id, product in products.items():

        if (
            product["sku"].lower() == sku.lower()
            and product_id != exclude_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un producto con ese SKU"
            )


def get_existing_product(product_id: int):
    """
    Recupera un producto y comprueba que esté disponible.
    """

    product = products.get(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    return product


# ==========================================
# GET: LISTAR PRODUCTOS
# ==========================================

@router.get("/", response_model=list[ProductResponse])
def get_products(
    category_id: int | None = None,
    product_status: ProductStatus | None = Query(
        default=None,
        alias="status"
    ),
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100)
):

    result = [
        product for product in products.values()
        if product["status"] != ProductStatus.INACTIVE
    ]

    # Filtrar por categoría
    if category_id is not None:
        result = [
            product for product in result
            if product["category_id"] == category_id
        ]

    # Filtrar por estado
    if product_status is not None:
        result = [
            product for product in result
            if product["status"] == product_status
        ]

    # Buscar por nombre
    if search:
        result = [
            product for product in result
            if search.lower() in product["name"].lower()
        ]

    # Paginación
    start = (page - 1) * limit

    return result[start:start + limit]


# ==========================================
# GET: PRODUCTOS DESTACADOS
# ==========================================

@router.get("/featured", response_model=list[ProductResponse])
def get_featured_products():

    return [
        product for product in products.values()
        if (
            product["is_featured"]
            and product["status"] == ProductStatus.ACTIVE
        )
    ]


# ==========================================
# GET: PRODUCTOS NUEVOS
# ==========================================

@router.get("/new", response_model=list[ProductResponse])
def get_new_products():

    return [
        product for product in products.values()
        if (
            product["is_new"]
            and product["status"] == ProductStatus.ACTIVE
        )
    ]


# ==========================================
# GET: CONSULTAR UN PRODUCTO
# ==========================================

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):

    product = get_existing_product(product_id)

    if product["status"] == ProductStatus.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    return product


# ==========================================
# POST: CREAR UN PRODUCTO
# ==========================================

@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(product: ProductCreate):

    global next_id

    # Comprobar categoría
    check_category(product.category_id)

    # Comprobar SKU
    check_sku(product.sku)

    # Crear producto
    now = datetime.now()

    new_product = {
        "id": next_id,
        **product.model_dump(),
        "created_at": now,
        "updated_at": now
    }

    products[next_id] = new_product

    next_id += 1

    return new_product


# ==========================================
# PUT: MODIFICAR UN PRODUCTO
# ==========================================

@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: int,
    product: ProductUpdate
):

    existing_product = get_existing_product(product_id)

    updated_data = product.model_dump(exclude_unset=True)

    # Comprobar campos obligatorios
    required_fields = {
        "category_id",
        "name",
        "sku",
        "price",
        "stock",
        "status",
        "is_featured",
        "is_new"
    }

    for field in required_fields:
        if field in updated_data and updated_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"El campo {field} no puede ser nulo"
            )

    # Comprobar categoría
    if "category_id" in updated_data:
        check_category(updated_data["category_id"])

    # Comprobar SKU
    if "sku" in updated_data:
        check_sku(
            updated_data["sku"],
            exclude_id=product_id
        )

    # Actualizar datos
    existing_product.update(updated_data)
    existing_product["updated_at"] = datetime.now()

    return existing_product


# ==========================================
# DELETE: DESACTIVAR UN PRODUCTO
# ==========================================

@router.delete("/{product_id}")
def delete_product(product_id: int):

    product = get_existing_product(product_id)

    if product["status"] == ProductStatus.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El producto ya está desactivado"
        )

    product["status"] = ProductStatus.INACTIVE
    product["updated_at"] = datetime.now()

    return {
        "message": "Producto desactivado correctamente",
        "product_id": product_id
    }
