from pydantic import BaseModel, ConfigDict, Field

from app.models.job import JobStatus
from app.schemas.driver import DriverRead
from app.schemas.truck import TruckRead


class JobBase(BaseModel):
    pickup_location: str = Field(..., min_length=2, max_length=255)
    delivery_location: str = Field(..., min_length=2, max_length=255)
    cargo_description: str = Field(..., min_length=2)
    status: JobStatus = JobStatus.PENDING
    assigned_truck_id: int | None = None
    assigned_driver_id: int | None = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    pickup_location: str | None = Field(default=None, min_length=2, max_length=255)
    delivery_location: str | None = Field(default=None, min_length=2, max_length=255)
    cargo_description: str | None = Field(default=None, min_length=2)
    status: JobStatus | None = None
    assigned_truck_id: int | None = None
    assigned_driver_id: int | None = None


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pickup_location: str
    delivery_location: str
    cargo_description: str
    status: JobStatus
    assigned_truck_id: int | None
    assigned_driver_id: int | None
    truck: TruckRead | None = None
    driver: DriverRead | None = None
