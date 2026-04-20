from pydantic import BaseModel, ConfigDict, Field

from app.models.truck import TruckStatus


class TruckBase(BaseModel):
    registration_number: str = Field(..., min_length=3, max_length=50)
    capacity: float = Field(..., gt=0)
    status: TruckStatus = TruckStatus.AVAILABLE


class TruckCreate(TruckBase):
    pass


class TruckUpdate(BaseModel):
    registration_number: str | None = Field(default=None, min_length=3, max_length=50)
    capacity: float | None = Field(default=None, gt=0)
    status: TruckStatus | None = None


class TruckRead(TruckBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
