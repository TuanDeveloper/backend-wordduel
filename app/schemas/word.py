from pydantic import BaseModel, ConfigDict, Field


class WordBase(BaseModel):
    term: str = Field(min_length=1, max_length=100)
    definition: str = Field(min_length=1, max_length=255)
    example: str | None = Field(default=None, max_length=500)
    context_sentence: str | None = Field(default=None, max_length=1000)


class WordCreate(WordBase):
    pass


class WordUpdate(BaseModel):
    term: str | None = Field(default=None, min_length=1, max_length=100)
    definition: str | None = Field(default=None, min_length=1, max_length=255)
    example: str | None = Field(default=None, max_length=500)
    context_sentence: str | None = Field(default=None, max_length=1000)


class WordResponse(WordBase):
    id: int
    word_set_id: int

    model_config = ConfigDict(from_attributes=True)


class WordSetBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)


class WordSetCreate(WordSetBase):
    words: list[WordCreate] = Field(default_factory=list, max_length=500)


class WordSetUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)


class WordSetResponse(WordSetBase):
    id: int
    creator_id: int | None = None
    words: list[WordResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class WordSetSummaryResponse(WordSetBase):
    id: int
    creator_id: int | None = None
    word_count: int = 0

    model_config = ConfigDict(from_attributes=True)

