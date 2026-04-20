from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.job import Job, JobStatus
from app.schemas.common import PaginatedResponse
from app.schemas.job import JobCreate, JobRead, JobUpdate
from app.services.job_service import (
    ensure_job_can_be_deleted,
    release_truck_if_idle,
    sync_truck_status,
    validate_assignment,
)

router = APIRouter(prefix="/jobs", tags=["Jobs"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=PaginatedResponse[JobRead])
def get_jobs(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    total = db.query(Job).count()
    items = db.query(Job).options(selectinload(Job.truck), selectinload(Job.driver)).offset(offset).limit(limit).all()
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=items)


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    truck, driver = validate_assignment(db, payload.assigned_truck_id, payload.assigned_driver_id)
    job = Job(**payload.model_dump())
    db.add(job)
    db.flush()
    sync_truck_status(job, truck)
    db.commit()
    job = db.scalar(
        select(Job)
        .options(selectinload(Job.truck), selectinload(Job.driver))
        .where(Job.id == job.id)
    )
    return job


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.scalar(
        select(Job)
        .options(selectinload(Job.truck), selectinload(Job.driver))
        .where(Job.id == job_id)
    )
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobRead)
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    old_truck = job.truck
    data = payload.model_dump(exclude_unset=True)
    truck_id = data.get("assigned_truck_id", job.assigned_truck_id)
    driver_id = data.get("assigned_driver_id", job.assigned_driver_id)
    truck, _driver = validate_assignment(db, truck_id, driver_id, current_job_id=job_id)

    for field, value in data.items():
        setattr(job, field, value)

    if old_truck and old_truck.id != job.assigned_truck_id:
        release_truck_if_idle(db, old_truck, exclude_job_id=job.id)
    sync_truck_status(job, truck or job.truck)

    db.commit()
    refreshed = db.scalar(
        select(Job)
        .options(selectinload(Job.truck), selectinload(Job.driver))
        .where(Job.id == job_id)
    )
    return refreshed


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    ensure_job_can_be_deleted(job)
    if job.truck:
        release_truck_if_idle(db, job.truck, exclude_job_id=job.id)

    db.delete(job)
    db.commit()
