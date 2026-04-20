from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.job import Job, JobStatus
from app.models.truck import Truck
from app.schemas.common import PaginatedResponse
from app.schemas.truck import TruckCreate, TruckRead, TruckUpdate
from app.services.truck_service import list_trucks

router = APIRouter(prefix="/trucks", tags=["Trucks"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=PaginatedResponse[TruckRead])
def get_trucks(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    total, items = list_trucks(db, limit, offset)
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=items)


@router.post("", response_model=TruckRead, status_code=status.HTTP_201_CREATED)
def create_truck(payload: TruckCreate, db: Session = Depends(get_db)):
    truck = Truck(**payload.model_dump())
    db.add(truck)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration number already exists",
        ) from exc
    db.refresh(truck)
    return truck


@router.get("/{truck_id}", response_model=TruckRead)
def get_truck(truck_id: int, db: Session = Depends(get_db)):
    truck = db.get(Truck, truck_id)
    if not truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found")
    return truck


@router.put("/{truck_id}", response_model=TruckRead)
def update_truck(truck_id: int, payload: TruckUpdate, db: Session = Depends(get_db)):
    truck = db.get(Truck, truck_id)
    if not truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found")

    active_job = db.scalar(
        select(Job).where(
            Job.assigned_truck_id == truck_id,
            Job.status.in_([JobStatus.ASSIGNED, JobStatus.IN_TRANSIT]),
        )
    )
    if active_job and payload.status and payload.status != truck.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Truck status is controlled by its active job",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(truck, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration number already exists",
        ) from exc
    db.refresh(truck)
    return truck


@router.delete("/{truck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_truck(truck_id: int, db: Session = Depends(get_db)):
    truck = db.get(Truck, truck_id)
    if not truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found")

    active_job = db.scalar(
        select(Job).where(
            Job.assigned_truck_id == truck_id,
            Job.status.in_([JobStatus.ASSIGNED, JobStatus.IN_TRANSIT]),
        )
    )
    if active_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Truck cannot be deleted while assigned to an active job",
        )

    db.delete(truck)
    db.commit()
