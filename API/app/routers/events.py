
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventStatus,
    EventType
)
from app.core.dependencies import get_current_admin


router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


# ==========================================
# ALMACENAMIENTO TEMPORAL EN MEMORIA
# ==========================================

events = {}
next_event_id = 1


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def get_existing_event(event_id: int):
    event = events.get(event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )

    return event


# ==========================================
# GET - LISTAR EVENTOS
# ==========================================

@router.get("/", response_model=list[EventResponse])
def get_events(
    event_status: EventStatus | None = Query(default=None),
    event_type: EventType | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100)
):
    result = list(events.values())

    if event_status is not None:
        result = [
            event for event in result
            if event["status"] == event_status
        ]

    if event_type is not None:
        result = [
            event for event in result
            if event["event_type"] == event_type
        ]

    result.sort(key=lambda event: event["event_date"])

    return result[skip:skip + limit]


# ==========================================
# GET - CONSULTAR EVENTO POR ID
# ==========================================

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int):
    return get_existing_event(event_id)


# ==========================================
# POST - CREAR EVENTO (ADMIN)
# ==========================================

@router.post(
    "/",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED
)
def create_event(
    event_data: EventCreate,
    current_admin: dict = Depends(get_current_admin)
):
    global next_event_id

    event = event_data.model_dump()

    now = datetime.now()

    event.update({
        "id": next_event_id,
        "status": EventStatus.DRAFT,
        "created_by": current_admin["id"],
        "created_at": now,
        "updated_at": now
    })

    events[next_event_id] = event
    next_event_id += 1

    return event


# ==========================================
# PUT - ACTUALIZAR EVENTO (ADMIN)
# ==========================================

@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    event = get_existing_event(event_id)

    if event["status"] in (
        EventStatus.CANCELLED,
        EventStatus.COMPLETED
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden modificar eventos cancelados o completados"
        )

    update_data = event_data.model_dump(exclude_unset=True)

    # Comprobar las fechas combinando los datos nuevos y existentes
    new_event_date = update_data.get(
        "event_date",
        event["event_date"]
    )

    new_end_date = update_data.get(
        "end_date",
        event["end_date"]
    )

    if new_end_date is not None and new_end_date <= new_event_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de finalización debe ser posterior a la fecha del evento"
        )

    for field, value in update_data.items():
        event[field] = value

    event["updated_at"] = datetime.now()

    return event


# ==========================================
# DELETE - CANCELAR EVENTO (ADMIN)
# ==========================================

@router.delete("/{event_id}")
def cancel_event(
    event_id: int,
    current_admin: dict = Depends(get_current_admin)
):
    event = get_existing_event(event_id)

    if event["status"] == EventStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El evento ya está cancelado"
        )

    if event["status"] == EventStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cancelar un evento completado"
        )

    event["status"] = EventStatus.CANCELLED
    event["updated_at"] = datetime.now()

    return {
        "message": "Evento cancelado correctamente",
        "event_id": event_id
    }
