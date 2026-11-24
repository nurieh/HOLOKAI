
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from collections import defaultdict

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status
)

from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderStatus
)

from app.schemas.user import UserRole
from app.schemas.product import ProductStatus

from app.core.dependencies import (
    get_current_user,
    get_current_admin
)

from app.routers.products import products


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# ==========================================
# ALMACENAMIENTO TEMPORAL DE PEDIDOS
# ==========================================

orders = {}
next_order_id = 1
next_item_id = 1


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def get_existing_order(order_id: int):
    order = orders.get(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )

    return order


def check_order_owner(order: dict, user: dict):
    """
    Comprueba que el pedido pertenece al usuario.
    """

    if (
        user["role"] != UserRole.ADMIN
        and order["user_id"] != user["id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar este pedido"
        )


def generate_order_number():
    """
    Genera un número de pedido único.
    """

    return f"HK-{datetime.now():%Y%m%d}-{uuid4().hex[:8].upper()}"


# ==========================================
# GET: LISTAR PEDIDOS
# ==========================================

@router.get("/", response_model=list[OrderResponse])
def get_orders(
    current_user: dict = Depends(get_current_user),
    order_status: OrderStatus | None = Query(
        default=None,
        alias="status"
    ),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100)
):
    result = list(orders.values())

    # Los clientes solamente pueden consultar sus pedidos
    if current_user["role"] != UserRole.ADMIN:
        result = [
            order for order in result
            if order["user_id"] == current_user["id"]
        ]

    # Filtrar por estado
    if order_status is not None:
        result = [
            order for order in result
            if order["status"] == order_status
        ]

    # Ordenar del más reciente al más antiguo
    result.sort(
        key=lambda order: order["created_at"],
        reverse=True
    )

    # Paginación
    start = (page - 1) * limit

    return result[start:start + limit]


# ==========================================
# GET: CONSULTAR PEDIDO POR ID
# ==========================================

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int = Path(gt=0),
    current_user: dict = Depends(get_current_user)
):
    order = get_existing_order(order_id)

    check_order_owner(order, current_user)

    return order


# ==========================================
# POST: CREAR PEDIDO
# ==========================================

@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    global next_order_id, next_item_id

    # Agrupar productos repetidos
    requested_quantities = defaultdict(int)

    for item in order_data.items:
        requested_quantities[item.product_id] += item.quantity

    # Comprobar productos y stock antes de modificar nada
    selected_products = {}

    for product_id, quantity in requested_quantities.items():

        product = products.get(product_id)

        if (
            product is None
            or product["status"] != ProductStatus.ACTIVE
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El producto {product_id} no existe o no está activo"
            )

        if product["stock"] < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Stock insuficiente para el producto "
                    f"'{product['name']}'. "
                    f"Stock disponible: {product['stock']}"
                )
            )

        selected_products[product_id] = product

    # Calcular importes y crear artículos
    now = datetime.now()
    order_items = []
    subtotal = Decimal("0.00")

    for product_id, quantity in requested_quantities.items():

        product = selected_products[product_id]

        unit_price = Decimal(str(product["price"]))
        item_subtotal = unit_price * quantity

        order_item = {
            "id": next_item_id,
            "order_id": next_order_id,
            "product_id": product_id,
            "product_name": product["name"],
            "product_sku": product["sku"],
            "unit_price": unit_price,
            "quantity": quantity,
            "subtotal": item_subtotal
        }

        order_items.append(order_item)

        subtotal += item_subtotal
        next_item_id += 1

    # Importes de momento sin descuentos ni gastos de envío
    discount = Decimal("0.00")
    shipping_cost = Decimal("0.00")
    total = subtotal - discount + shipping_cost

    # Descontar stock
    for product_id, quantity in requested_quantities.items():
        selected_products[product_id]["stock"] -= quantity

    # Crear pedido
    new_order = {
        "id": next_order_id,
        "order_number": generate_order_number(),
        "user_id": current_user["id"],
        "coupon_id": None,

        "recipient_name": order_data.recipient_name,
        "phone": order_data.phone,
        "street": order_data.street,
        "city": order_data.city,
        "postal_code": order_data.postal_code,
        "province": order_data.province,
        "country": order_data.country,

        "subtotal": subtotal,
        "discount": discount,
        "shipping_cost": shipping_cost,
        "total": total,

        "status": OrderStatus.PENDING,

        "items": order_items,

        "created_at": now,
        "updated_at": now
    }

    orders[next_order_id] = new_order
    next_order_id += 1

    return new_order


# ==========================================
# PUT: ACTUALIZAR ESTADO DEL PEDIDO
# SOLO ADMINISTRADORES
# ==========================================

@router.put(
    "/{order_id}",
    response_model=OrderResponse
)
def update_order(
    order_data: OrderUpdate,
    order_id: int = Path(gt=0),
    current_admin: dict = Depends(get_current_admin)
):
    order = get_existing_order(order_id)

    if order["status"] == OrderStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar un pedido cancelado"
        )

    if order["status"] == OrderStatus.DELIVERED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar un pedido entregado"
        )

    if order_data.status == OrderStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utiliza el endpoint de cancelación para cancelar el pedido"
        )

    order["status"] = order_data.status
    order["updated_at"] = datetime.now()

    return order


# ==========================================
# POST: CANCELAR PEDIDO
# ==========================================

@router.post("/{order_id}/cancel")
def cancel_order(
    order_id: int = Path(gt=0),
    current_user: dict = Depends(get_current_user)
):
    order = get_existing_order(order_id)

    check_order_owner(order, current_user)

    is_admin = current_user["role"] == UserRole.ADMIN

    if order["status"] in (
        OrderStatus.CANCELLED,
        OrderStatus.DELIVERED
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este pedido no se puede cancelar"
        )

    # Los clientes solamente pueden cancelar pedidos pendientes
    if (
        not is_admin
        and order["status"] != OrderStatus.PENDING
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Solo puedes cancelar pedidos que estén "
                "en estado PENDING"
            )
        )

    # Restaurar stock de los productos
    for item in order["items"]:
        product = products.get(item["product_id"])

        if product is not None:
            product["stock"] += item["quantity"]

    order["status"] = OrderStatus.CANCELLED
    order["updated_at"] = datetime.now()

    return {
        "message": "Pedido cancelado correctamente",
        "order_id": order_id,
        "order_number": order["order_number"]
    }
