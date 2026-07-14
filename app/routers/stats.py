from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student
from app.schemas import StatsResponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)) -> StatsResponse:
    total = db.scalar(select(func.count()).select_from(Student)) or 0
    male = (
        db.scalar(
            select(func.count())
            .select_from(Student)
            .where(Student.gender.is_(False))
        )
        or 0
    )
    female = (
        db.scalar(
            select(func.count()).select_from(Student).where(Student.gender.is_(True))
        )
        or 0
    )
    return StatsResponse(total=total, male=male, female=female)
