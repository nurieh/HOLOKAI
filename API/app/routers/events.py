
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate, EventResponse


router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


# 1. CREAR EVENTO
@router.post("/", response_model=EventResponse)
def create_event(event: EventCreate, db: Session = Depends(get_db)):

    new_event = Event(**event.model_dump())

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


# 2. CONSULTAR TODOS LOS EVENTOS
@router.get("/", response_model=list[EventResponse])
def get_events(db: Session = Depends(get_db)):

    events = db.query(Event).all()

    return events


# 3. CONSULTAR UN EVENTO POR ID
@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):

    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Evento no encontrado"
        )

    return event


# 4. MODIFICAR UN EVENTO
@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db)
):

    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Evento no encontrado"
        )

    update_data = event_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)

    return event


# 5. ELIMINAR (CANCELAR) UN EVENTO
@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):

    event = db.query(Event).filter(Event.id == event_id).first()

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Evento no encontrado"
        )

    event.status = "CANCELLED"

    db.commit()

    return {
        "message": "Evento cancelado correctamente"
    }
