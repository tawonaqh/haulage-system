from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.driver import Driver
from app.models.job import Job, JobStatus
from app.models.truck import Truck, TruckStatus

ACTIVE_JOB_STATUSES = {JobStatus.ASSIGNED, JobStatus.IN_TRANSIT}


def list_jobs(db: Session, limit: int, offset: int) -> tuple[int, list[Job]]:
    total = db.scalar(select(func.count()).select_from(Job)) or 0
    items = db.scalars(select(Job).offset(offset).limit(limit)).all()
    return total, list(items)


def validate_assignment(
    db: Session,
    truck_id: int | None,
    driver_id: int | None,
    current_job_id: int | None = None,
) -> tuple[Truck | None, Driver | None]:
    truck = None
    driver = None

    if truck_id is not None:
        truck = db.get(Truck, truck_id)
        if not truck:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found")

        # Allow the truck if it's already assigned to the job being updated
        already_assigned_to_current = (
            current_job_id is not None
            and db.scalar(
                select(Job).where(
                    Job.id == current_job_id,
                    Job.assigned_truck_id == truck_id,
                )
            )
            is not None
        )
        if not already_assigned_to_current and truck.status in {TruckStatus.IN_TRANSIT, TruckStatus.MAINTENANCE}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Truck is not available for assignment",
            )

    if driver_id is not None:
        driver = db.get(Driver, driver_id)
        if not driver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
        stmt = select(Job).where(
            Job.assigned_driver_id == driver_id,
            Job.status.in_(ACTIVE_JOB_STATUSES),
        )
        if current_job_id is not None:
            stmt = stmt.where(Job.id != current_job_id)
        active_job = db.scalar(stmt)
        if active_job:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver already has an active job",
            )

    return truck, driver


def sync_truck_status(job: Job, truck: Truck | None) -> None:
    if not truck:
        return

    if job.status in {JobStatus.ASSIGNED, JobStatus.IN_TRANSIT}:
        truck.status = TruckStatus.IN_TRANSIT
    elif job.status in {JobStatus.COMPLETED, JobStatus.CANCELLED, JobStatus.PENDING}:
        truck.status = TruckStatus.AVAILABLE


def release_truck_if_idle(db: Session, truck: Truck | None, exclude_job_id: int | None = None) -> None:
    if not truck or truck.status == TruckStatus.MAINTENANCE:
        return

    stmt = select(Job).where(
        Job.assigned_truck_id == truck.id,
        Job.status.in_(ACTIVE_JOB_STATUSES),
    )
    if exclude_job_id is not None:
        stmt = stmt.where(Job.id != exclude_job_id)

    still_active = db.scalar(stmt)
    if not still_active:
        truck.status = TruckStatus.AVAILABLE


def ensure_job_can_be_deleted(job: Job) -> None:
    if job.status in ACTIVE_JOB_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active jobs cannot be deleted",
        )
