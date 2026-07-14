import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.errors import AppError
from app.models import Charm, ExHave, ExWant, Have, Student, Want
from app.schemas import StudentCreate, StudentRead, StudentUpdate

router = APIRouter(prefix="/students", tags=["students"])


def _load_student(db: Session, student_id: str) -> Student | None:
    return db.scalar(
        select(Student)
        .where(Student.student_id == student_id)
        .options(
            selectinload(Student.have_charms).selectinload(Have.charm),
            selectinload(Student.want_charms).selectinload(Want.charm),
            selectinload(Student.ex_have),
            selectinload(Student.ex_want),
        )
    )


def _to_student_read(student: Student) -> StudentRead:
    return StudentRead(
        student_id=student.student_id,
        name=student.name,
        gender=student.gender,
        age=student.age,
        mbti=student.mbti,
        have_charms=[
            relation.charm for relation in student.have_charms if relation.charm
        ],
        want_charms=[
            relation.charm for relation in student.want_charms if relation.charm
        ],
        ex_have=student.ex_have.charm if student.ex_have else None,
        ex_want=student.ex_want.charm if student.ex_want else None,
    )


def _ensure_charms_exist(db: Session, charm_ids: list[uuid.UUID]) -> None:
    if not charm_ids:
        return
    existing = set(
        db.scalars(select(Charm.charm_id).where(Charm.charm_id.in_(charm_ids))).all()
    )
    missing = [str(charm_id) for charm_id in charm_ids if charm_id not in existing]
    if missing:
        raise AppError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR",
            message=f"Unknown charm_id(s): {', '.join(missing)}",
        )


def _set_have_charms(
    db: Session, student: Student, charm_ids: list[uuid.UUID]
) -> None:
    _ensure_charms_exist(db, charm_ids)
    student.have_charms.clear()
    db.flush()
    student.have_charms.extend(
        [Have(student_id=student.student_id, charm_id=charm_id) for charm_id in charm_ids]
    )


def _set_want_charms(
    db: Session, student: Student, charm_ids: list[uuid.UUID]
) -> None:
    _ensure_charms_exist(db, charm_ids)
    student.want_charms.clear()
    db.flush()
    student.want_charms.extend(
        [Want(student_id=student.student_id, charm_id=charm_id) for charm_id in charm_ids]
    )


def _set_ex_have(db: Session, student: Student, charm: str | None) -> None:
    if charm is None or not charm.strip():
        if student.ex_have is not None:
            db.delete(student.ex_have)
            student.ex_have = None
        return
    if student.ex_have is None:
        student.ex_have = ExHave(student_id=student.student_id, charm=charm.strip())
    else:
        student.ex_have.charm = charm.strip()


def _set_ex_want(db: Session, student: Student, charm: str | None) -> None:
    if charm is None or not charm.strip():
        if student.ex_want is not None:
            db.delete(student.ex_want)
            student.ex_want = None
        return
    if student.ex_want is None:
        student.ex_want = ExWant(student_id=student.student_id, charm=charm.strip())
    else:
        student.ex_want.charm = charm.strip()


@router.get("", response_model=list[StudentRead])
def list_students(db: Session = Depends(get_db)) -> list[StudentRead]:
    students = db.scalars(
        select(Student)
        .options(
            selectinload(Student.have_charms).selectinload(Have.charm),
            selectinload(Student.want_charms).selectinload(Want.charm),
            selectinload(Student.ex_have),
            selectinload(Student.ex_want),
        )
        .order_by(Student.student_id)
    ).all()
    return [_to_student_read(student) for student in students]


@router.get("/{student_id}", response_model=StudentRead)
def get_student(student_id: str, db: Session = Depends(get_db)) -> StudentRead:
    student = _load_student(db, student_id)
    if student is None:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message="Student not found",
        )
    return _to_student_read(student)


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)) -> StudentRead:
    if _load_student(db, payload.student_id) is not None:
        raise AppError(
            status_code=status.HTTP_409_CONFLICT,
            code="DUPLICATE_STUDENT",
            message="이미 접수된 학번입니다.",
        )

    student = Student(
        student_id=payload.student_id,
        name=payload.name,
        gender=payload.gender,
        age=payload.age,
        mbti=payload.mbti,
    )
    db.add(student)
    db.flush()

    _set_have_charms(db, student, payload.have_charm_ids)
    _set_want_charms(db, student, payload.want_charm_ids)
    if payload.ex_have is not None:
        _set_ex_have(db, student, payload.ex_have)
    if payload.ex_want is not None:
        _set_ex_want(db, student, payload.ex_want)
    db.commit()

    created = _load_student(db, payload.student_id)
    assert created is not None
    return _to_student_read(created)


@router.patch("/{student_id}", response_model=StudentRead)
def update_student(
    student_id: str, payload: StudentUpdate, db: Session = Depends(get_db)
) -> StudentRead:
    student = _load_student(db, student_id)
    if student is None:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message="Student not found",
        )

    data = payload.model_dump(exclude_unset=True)
    have_charm_ids = data.pop("have_charm_ids", None)
    want_charm_ids = data.pop("want_charm_ids", None)
    fields_set = payload.model_fields_set
    ex_have = data.pop("ex_have", None) if "ex_have" in fields_set else None
    ex_want = data.pop("ex_want", None) if "ex_want" in fields_set else None

    for field, value in data.items():
        setattr(student, field, value)

    if have_charm_ids is not None:
        _set_have_charms(db, student, have_charm_ids)
    if want_charm_ids is not None:
        _set_want_charms(db, student, want_charm_ids)
    if "ex_have" in fields_set:
        _set_ex_have(db, student, ex_have)
    if "ex_want" in fields_set:
        _set_ex_want(db, student, ex_want)

    db.commit()
    updated = _load_student(db, student_id)
    assert updated is not None
    return _to_student_read(updated)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: str, db: Session = Depends(get_db)) -> None:
    student = db.get(Student, student_id)
    if student is None:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message="Student not found",
        )
    db.delete(student)
    db.commit()
