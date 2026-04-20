from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.truck import Truck


def list_trucks(db: Session, limit: int, offset: int) -> tuple[int, list[Truck]]:
    total = db.scalar(select(func.count()).select_from(Truck)) or 0
    items = db.scalars(select(Truck).offset(offset).limit(limit)).all()
    return total, list(items)
