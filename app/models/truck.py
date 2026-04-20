import enum

from sqlalchemy import Enum, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TruckStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_TRANSIT = "in_transit"
    MAINTENANCE = "maintenance"


class Truck(Base):
    __tablename__ = "trucks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    registration_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    capacity: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[TruckStatus] = mapped_column(
        Enum(TruckStatus, name="truck_status"),
        default=TruckStatus.AVAILABLE,
        nullable=False,
    )

    jobs = relationship("Job", back_populates="truck")
