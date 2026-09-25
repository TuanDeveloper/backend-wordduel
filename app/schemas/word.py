from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class WordBase(BaseModel):
    term: str
    definition: str
    example: Optional[str] = None


class WordCreate(WordBase):
    pass


class WordUpdate(BaseModel):
    term: Optional[str] = None
    definition: Optional[str] = None
    example: Optional[str] = None


class WordResponse(WordBase):
    id: int
    word_set_id: int

    model_config = ConfigDict(from_attributes=True)


class WordSetBase(BaseModel):
    title: str
    description: Optional[str] = None


class WordSetCreate(WordSetBase):
    words: List[WordCreate] = []


class WordSetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class WordSetResponse(WordSetBase):
    id: int
    creator_id: Optional[int] = None
    words: List[WordResponse] = []

    model_config = ConfigDict(from_attributes=True)

