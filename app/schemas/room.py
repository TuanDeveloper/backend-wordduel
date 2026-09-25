from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserResponse


class RoomPlayerResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    score: int
    is_ready: bool
    joined_at: Optional[datetime] = None
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class RoomCreate(BaseModel):
    word_set_id: int


class SubmitRequest(BaseModel):
    word_id: int
    submitted_answer: str


class RoomResponse(BaseModel):
    id: int
    code: str
    host_id: int
    word_set_id: int
    status: str
    created_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    players: List[RoomPlayerResponse] = []

    model_config = ConfigDict(from_attributes=True)
