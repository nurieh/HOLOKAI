from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentStatus,
)
from app.schemas.order import OrderStatus
from app.schemas.user import UserRole
from app.core.dependencies import get_current_user, get_current_admin
from app.routers.orders import orders


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


# Almacenamiento temporal en memoria
payments = {}

next_payment_id = 1


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def get_existing_payment(payment_id: int):
    payment = payments.get(payment_id)

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado"
        )

    return payment


def get_existing_order(order_id: int):
    order = orders.get(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )

    return order


def check_payment_owner(payment, user):
    order = get_existing_order(payment["order_id"])

    if user["role"] != UserRole.ADMIN and order["user_id"] != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar este pago"
        )

    return payment


def generate_transaction_reference():
    return f"HK-PAY-{uuid4().hex[:16].upper()}"


# ==========================================
# GET - LISTAR PAGOS
# ==========================================

@router.get("/", response_model=list[PaymentResponse])
def get_payments(
    payment_status: PaymentStatus | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    result = list(payments.values())

    # Los clientes solo ven sus propios pagos
    if current_user["role"] != UserRole.ADMIN:
        result = [
            payment for payment in result
            if orders.get(payment["order_id"], {}).get("user_id")
            == current_user["id"]
        ]

    if payment_status is not None:
        result = [
            payment for payment in result
            if payment["status"] == payment_status
        ]

    return result[skip:skip + limit]


# ==========================================
# GET - CONSULTAR PAGO POR ID
# ==========================================

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    current_user: dict = Depends(get_current_user)
):
    payment = get_existing_payment(payment_id)

    check_payment_owner(payment, current_user)

    return payment


# ==========================================
# POST - CREAR PAGO
# ==========================================

@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_payment(
    payment_data: PaymentCreate,
    current_user: dict = Depends(get_current_user)
):
    global next_payment_id

    order = get_existing_order(payment_data.order_id)

    # Comprobar que el pedido pertenece al usuario
    if (
        current_user["role"] != UserRole.ADMIN
        and order["user_id"] != current_user["id"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes realizar pagos de pedidos de otros usuarios"
        )

    # Solo se pueden pagar pedidos pendientes
    if order["status"] != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El pedido no está pendiente de pago"
        )

    # Evitar pagos duplicados pendientes o aprobados
    for existing_payment in payments.values():
        if existing_payment["order_id"] == payment_data.order_id:
            if existing_payment["status"] in (
                PaymentStatus.PENDING,
                PaymentStatus.APPROVED
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Este pedido ya tiene un pago pendiente o aprobado"
                )

    payment = {
        "id": next_payment_id,
        "order_id": payment_data.order_id,
        "payment_method": payment_data.payment_method,
        "amount": Decimal(str(order["total"])),
        "status": PaymentStatus.PENDING,
        "transaction_reference": generate_transaction_reference(),
        "created_at": datetime.now()
    }

    payments[next_payment_id] = payment
    next_payment_id += 1

    return payment


# ==========================================
# PUT - ACTUALIZAR ESTADO DEL PAGO (ADMIN)
# ==========================================

@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    payment = get_existing_payment(payment_id)
    order = get_existing_order(payment["order_id"])

    current_status = payment["status"]
    new_status = payment_data.status

    if current_status == new_status:
        return payment

    # Transiciones permitidas
    if current_status == PaymentStatus.PENDING:
        allowed_statuses = (
            PaymentStatus.APPROVED,
            PaymentStatus.REJECTED
        )
    elif current_status == PaymentStatus.APPROVED:
        allowed_statuses = (PaymentStatus.REFUNDED,)
    else:
        allowed_statuses = ()

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede cambiar el pago de {current_status.value} a {new_status.value}"
        )

    # Un pago solo puede aprobarse si el pedido sigue pendiente
    if (
        new_status == PaymentStatus.APPROVED
        and order["status"] != OrderStatus.PENDING
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El pedido ya no está pendiente"
        )

    payment["status"] = new_status

    # Al aprobar el pago, confirmar el pedido
    if new_status == PaymentStatus.APPROVED:
        order["status"] = OrderStatus.CONFIRMED
        order["updated_at"] = datetime.now()

    payment["updated_at"] = datetime.now()

    return payment