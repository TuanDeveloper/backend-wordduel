from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    word_set_id: int | None = Field(default=None, gt=0)
    word_set_ids: list[int] | None = Field(default=None, min_length=1, max_length=100)
    word_count: int | None = Field(default=None, ge=1, le=500)
    time_per_question: int | None = Field(default=20, ge=5, le=300)
    question_count: int | None = Field(default=None, ge=1, le=500)
    game_mode: Literal["classic", "reverse", "multiple_choice", "listen_choice", "listen_spelling", "fill_blank", "speak"] = "classic"
    board_game_mode: Literal["monopoly", "boss", "race", "territory"] | None = None
    points_per_correct: int = Field(default=1, ge=0, le=1000)

    @model_validator(mode="after")
    def normalize_word_set_ids(self):
        ids = self.word_set_ids or ([self.word_set_id] if self.word_set_id else [])
        ids = list(dict.fromkeys(ids))
        if not ids:
            raise ValueError("Chá»n Ã­t nháº¥t má»™t bá»™ tá»« vá»±ng")
        self.word_set_ids = ids
        self.word_set_id = ids[0]
        return self


class RoomSettingsUpdate(BaseModel):
    game_mode: Literal["classic", "reverse", "multiple_choice", "listen_choice", "listen_spelling", "fill_blank", "speak"] | None = None
    board_game_mode: Literal["monopoly", "boss", "race", "territory"] | None = None
    time_per_question: int | None = Field(default=None, ge=5, le=300)
    question_count: int | None = Field(default=None, ge=1, le=500)
    points_per_correct: int | None = Field(default=None, ge=0, le=1000)


class SubmitRequest(BaseModel):
    word_id: int = Field(gt=0)
    submitted_answer: str = Field(max_length=255)
    question_index: int = Field(default=0, ge=0, le=499)


class BoardActionRequest(BaseModel):
    action: Literal["roll", "answer"]
    answer: str | None = Field(default=None, max_length=1000)


class SoloStartRequest(BaseModel):
    source: Literal["word_set", "library"] = "word_set"
    word_set_id: int | None = Field(default=None, gt=0)
    word_count: int | None = Field(default=None, ge=1, le=500)
    time_per_question: int | None = Field(default=20, ge=5, le=300)
    question_count: int | None = Field(default=None, ge=1, le=500)
    game_mode: Literal["classic", "reverse", "multiple_choice", "listen_choice", "listen_spelling", "fill_blank", "speak"] = "classic"


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
    word_set_ids: list[int] = Field(default_factory=list)
    points_per_correct: int = 1
    word_count: int | None = None
    time_per_question: int | None = None
    question_count: int | None = None
    game_mode: str = "classic"
    board_game_mode: str | None = None
    status: str
    created_at: datetime | None = None
    finished_at: datetime | None = None
    players: list[RoomPlayerResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
