from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.driver import Driver


def list_drivers(db: Session, limit: int, offset: int) -> tuple[int, list[Driver]]:
    total = db.scalar(select(func.count()).select_from(Driver)) or 0
    items = db.scalars(select(Driver).offset(offset).limit(limit)).all()
    return total, list(items)
