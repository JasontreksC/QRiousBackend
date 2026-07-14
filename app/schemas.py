import re
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class CharmItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    charm_id: uuid.UUID
    name: str | None = None


class CharmListResponse(BaseModel):
    charms: list[CharmItem]


class StatsResponse(BaseModel):
    total: int
    male: int
    female: int


class SurveyCreate(BaseModel):
    student_id: str
    name: str
    gender: bool
    age: int = Field(ge=0)
    mbti: str
    have_charm_ids: list[uuid.UUID] = Field(min_length=1)
    want_charm_ids: list[uuid.UUID] = Field(min_length=1)
    ex_have: str | None = None
    ex_want: str | None = None

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, value: str) -> str:
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("student_id must be exactly 10 digits")
        return value

    @field_validator("mbti")
    @classmethod
    def validate_mbti(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not re.fullmatch(r"[EI][NS][FT][JP]", normalized):
            raise ValueError("mbti must be a valid 4-letter MBTI code")
        return normalized

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("name must not be empty")
        return stripped

    @field_validator("ex_have", "ex_want")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class SurveyCreateResponse(BaseModel):
    student_id: str


# --- Legacy CRUD schemas (students / charms admin) ---


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
    ex_have: str | None = None
    ex_want: str | None = None


class StudentUpdate(BaseModel):
    name: str | None = None
    gender: bool | None = None
    age: int | None = Field(default=None, ge=0)
    mbti: str | None = None
    have_charm_ids: list[uuid.UUID] | None = None
    want_charm_ids: list[uuid.UUID] | None = None
    ex_have: str | None = None
    ex_want: str | None = None


class StudentRead(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    student_id: str
    have_charms: list[CharmRead] = Field(default_factory=list)
    want_charms: list[CharmRead] = Field(default_factory=list)
    ex_have: str | None = None
    ex_want: str | None = None


class HealthResponse(BaseModel):
    status: str
    database: str
