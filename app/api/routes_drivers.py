from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.driver import Driver
from app.models.job import Job, JobStatus
from app.schemas.common import PaginatedResponse
from app.schemas.driver import DriverCreate, DriverRead, DriverUpdate
from app.services.driver_service import list_drivers

router = APIRouter(prefix="/drivers", tags=["Drivers"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=PaginatedResponse[DriverRead])
def get_drivers(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    total, items = list_drivers(db, limit, offset)
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=items)


@router.post("", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
def create_driver(payload: DriverCreate, db: Session = Depends(get_db)):
    driver = Driver(**payload.model_dump())
    db.add(driver)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="License number already exists",
        ) from exc
    db.refresh(driver)
    return driver


@router.get("/{driver_id}", response_model=DriverRead)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    return driver


@router.put("/{driver_id}", response_model=DriverRead)
def update_driver(driver_id: int, payload: DriverUpdate, db: Session = Depends(get_db)):
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="License number already exists",
        ) from exc
    db.refresh(driver)
    return driver


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")

    active_job = db.scalar(
        select(Job).where(
            Job.assigned_driver_id == driver_id,
            Job.status.in_([JobStatus.ASSIGNED, JobStatus.IN_TRANSIT]),
        )
    )
    if active_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver cannot be deleted while handling an active job",
        )

    db.delete(driver)
    db.commit()
