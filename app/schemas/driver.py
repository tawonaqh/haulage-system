from pydantic import BaseModel, ConfigDict, Field


class DriverBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    license_number: str = Field(..., min_length=3, max_length=50)
    phone_number: str = Field(..., min_length=7, max_length=30)


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    license_number: str | None = Field(default=None, min_length=3, max_length=50)
    phone_number: str | None = Field(default=None, min_length=7, max_length=30)


class DriverRead(DriverBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
