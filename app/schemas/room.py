from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class RoomPlayerUserResponse(BaseModel):
    username: str

    model_config = ConfigDict(from_attributes=True)


class RoomPlayerResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    score: int
    is_ready: bool
    joined_at: datetime | None = None
    user: RoomPlayerUserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class RoomCreate(BaseModel):
    word_set_id: int = Field(gt=0)
    word_count: int | None = Field(default=None, ge=1, le=500)
    time_per_question: int | None = Field(default=20, ge=5, le=300)
    question_count: int | None = Field(default=None, ge=1, le=500)


class SubmitRequest(BaseModel):
    word_id: int = Field(gt=0)
    submitted_answer: str = Field(max_length=255)
    question_index: int = Field(default=0, ge=0, le=499)


class SoloStartRequest(BaseModel):
    source: Literal["word_set", "library"] = "word_set"
    word_set_id: int | None = Field(default=None, gt=0)
    word_count: int | None = Field(default=None, ge=1, le=500)
    time_per_question: int | None = Field(default=20, ge=5, le=300)
    question_count: int | None = Field(default=None, ge=1, le=500)


class SoloSubmitRequest(BaseModel):
    word_id: int = Field(gt=0)
    question_index: int = Field(ge=0, le=499)
    submitted_answer: str = Field(max_length=255)
    response_time_ms: int = Field(default=0, ge=0, le=86_400_000)


class RoomResponse(BaseModel):
    id: int
    code: str
    host_id: int
    word_set_id: int
    word_count: int | None = None
    time_per_question: int | None = None
    question_count: int | None = None
    status: str
    created_at: datetime | None = None
    finished_at: datetime | None = None
    players: list[RoomPlayerResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
