import uuid

from pydantic import BaseModel, ConfigDict, Field


class CharmBase(BaseModel):
    name: str | None = None


class CharmCreate(CharmBase):
    pass


class CharmUpdate(BaseModel):
    name: str | None = None


class CharmRead(CharmBase):
    model_config = ConfigDict(from_attributes=True)

    charm_id: uuid.UUID


class StudentBase(BaseModel):
    name: str | None = None
    gender: bool | None = False
    age: int | None = Field(default=None, ge=0)
    mbti: str | None = None


class StudentCreate(StudentBase):
    student_id: str
    have_charm_ids: list[uuid.UUID] = Field(default_factory=list)
    want_charm_ids: list[uuid.UUID] = Field(default_factory=list)


class StudentUpdate(BaseModel):
    name: str | None = None
    gender: bool | None = None
    age: int | None = Field(default=None, ge=0)
    mbti: str | None = None
    have_charm_ids: list[uuid.UUID] | None = None
    want_charm_ids: list[uuid.UUID] | None = None


class StudentRead(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    student_id: str
    have_charms: list[CharmRead] = Field(default_factory=list)
    want_charms: list[CharmRead] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    database: str
