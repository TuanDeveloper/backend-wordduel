from datetime import datetime
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


class SubmitRequest(BaseModel):
    word_id: int = Field(gt=0)
    submitted_answer: str = Field(max_length=255)


class RoomResponse(BaseModel):
    id: int
    code: str
    host_id: int
    word_set_id: int
    status: str
    created_at: datetime | None = None
    finished_at: datetime | None = None
    players: list[RoomPlayerResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
