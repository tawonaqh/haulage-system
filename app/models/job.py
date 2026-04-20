import enum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    pickup_location: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_location: Mapped[str] = mapped_column(String(255), nullable=False)
    cargo_description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"),
        default=JobStatus.PENDING,
        nullable=False,
    )
    assigned_truck_id: Mapped[int | None] = mapped_column(ForeignKey("trucks.id"), nullable=True)
    assigned_driver_id: Mapped[int | None] = mapped_column(ForeignKey("drivers.id"), nullable=True)

    truck = relationship("Truck", back_populates="jobs")
    driver = relationship("Driver", back_populates="jobs")
