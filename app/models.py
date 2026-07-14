import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Student(Base):
    __tablename__ = "student"

    student_id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    gender: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mbti: Mapped[str | None] = mapped_column(Text, nullable=True)

    have_charms: Mapped[list["Have"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    want_charms: Mapped[list["Want"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )


class Charm(Base):
    __tablename__ = "charm"

    charm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str | None] = mapped_column(Text, nullable=True)

    have_students: Mapped[list["Have"]] = relationship(
        back_populates="charm", cascade="all, delete-orphan"
    )
    want_students: Mapped[list["Want"]] = relationship(
        back_populates="charm", cascade="all, delete-orphan"
    )


class Have(Base):
    __tablename__ = "have"

    student_id: Mapped[str] = mapped_column(
        Text, ForeignKey("student.student_id", ondelete="CASCADE"), primary_key=True
    )
    charm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("charm.charm_id", ondelete="CASCADE"),
        primary_key=True,
    )

    student: Mapped["Student"] = relationship(back_populates="have_charms")
    charm: Mapped["Charm"] = relationship(back_populates="have_students")


class Want(Base):
    __tablename__ = "want"

    student_id: Mapped[str] = mapped_column(
        Text, ForeignKey("student.student_id", ondelete="CASCADE"), primary_key=True
    )
    charm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("charm.charm_id", ondelete="CASCADE"),
        primary_key=True,
    )

    student: Mapped["Student"] = relationship(back_populates="want_charms")
    charm: Mapped["Charm"] = relationship(back_populates="want_students")
