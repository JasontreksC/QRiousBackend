import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import AppError
from app.models import Charm, ExHave, ExWant, Have, Student, Want
from app.schemas import SurveyCreate, SurveyCreateResponse

router = APIRouter(prefix="/surveys", tags=["surveys"])


def _ensure_charms_exist(db: Session, charm_ids: list[uuid.UUID], field: str) -> None:
    unique_ids = list(dict.fromkeys(charm_ids))
    existing = set(
        db.scalars(select(Charm.charm_id).where(Charm.charm_id.in_(unique_ids))).all()
    )
    missing = [str(charm_id) for charm_id in unique_ids if charm_id not in existing]
    if missing:
        raise AppError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR",
            message=f"{field} contains unknown charm_id(s): {', '.join(missing)}",
        )


@router.post("", response_model=SurveyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_survey(
    payload: SurveyCreate, db: Session = Depends(get_db)
) -> SurveyCreateResponse:
    exists = db.scalar(
        select(func.count()).select_from(Student).where(
            Student.student_id == payload.student_id
        )
    )
    if exists:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="DUPLICATE_STUDENT",
            message="이미 접수된 학번입니다.",
        )

    _ensure_charms_exist(db, payload.have_charm_ids, "have_charm_ids")
    _ensure_charms_exist(db, payload.want_charm_ids, "want_charm_ids")

    try:
        student = Student(
            student_id=payload.student_id,
            name=payload.name,
            gender=payload.gender,
            age=payload.age,
            mbti=payload.mbti,
        )
        db.add(student)
        db.flush()

        db.add_all(
            [
                Have(student_id=payload.student_id, charm_id=charm_id)
                for charm_id in dict.fromkeys(payload.have_charm_ids)
            ]
        )
        db.add_all(
            [
                Want(student_id=payload.student_id, charm_id=charm_id)
                for charm_id in dict.fromkeys(payload.want_charm_ids)
            ]
        )

        if payload.ex_have is not None:
            db.add(ExHave(student_id=payload.student_id, charm=payload.ex_have))
        if payload.ex_want is not None:
            db.add(ExWant(student_id=payload.student_id, charm=payload.ex_want))

        db.commit()
    except Exception:
        db.rollback()
        raise

    return SurveyCreateResponse(student_id=payload.student_id)
