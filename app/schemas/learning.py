from datetime import datetime

from pydantic import BaseModel, Field


class SaveWordRequest(BaseModel):
    word_id: int = Field(gt=0)
    note: str | None = Field(default=None, max_length=500)


class SavedWordResponse(BaseModel):
    id: int
    word_id: int
    note: str | None = None
    created_at: datetime
    word: dict
