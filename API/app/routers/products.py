
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# DATOS TEMPORALES PARA REALIZAR PRUEBAS
products = {
    1: {
        "id": 1,
        "name": "Pokémon Booster Pack",
        "description": "Sobre de cartas coleccionables",
        "price": 5.99,
        "stock": 25,
        "category_id": 2,
        "image_url": None,
        "is_active": True
    },
    2: {
        "id": 2,
        "name": "Magic Commander Deck",
        "description": "Mazo de Magic The Gathering",
        "price": 39.99,
        "stock": 10,
        "category_id": 3,
        "image_url": None,
        "is_active": True
    }
}

next_id = 3


# GET: Mostrar todos los productos
@router.get("/", response_model=list[ProductResponse])
def get_products(
    category_id: int | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100)
):
    result = [
        product for product in products.values()
        if product["is_active"]
    ]

    if category_id is not None:
        result = [
            product for product in result
            if product["category_id"] == category_id
        ]

    start = (page - 1) * limit
    return result[start:start + limit]


# GET: Mostrar un producto
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    product = products.get(product_id)

    if not product or not product["is_active"]:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    return product


# POST: Crear un producto
@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(product: ProductCreate):
    global next_id

    new_product = {
        "id": next_id,
        **product.model_dump(),
        "is_active": True
    }

    products[next_id] = new_product
    next_id += 1

    return new_product


# PUT: Modificar un producto
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate):
    if product_id not in products or not products[product_id]["is_active"]:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    updated_data = product.model_dump(exclude_unset=True)

    products[product_id].update(updated_data)

    return products[product_id]


# DELETE: Desactivar un producto
@router.delete("/{product_id}")
def delete_product(product_id: int):
    if product_id not in products or not products[product_id]["is_active"]:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    products[product_id]["is_active"] = False

    return {
        "message": "Producto desactivado correctamente"
    }


# GET: Productos destacados
@router.get("/featured", response_model=list[ProductResponse])
def get_featured_products():
    return [
        product for product in products.values()
        if product["is_active"] and product["stock"] > 0
    ]
