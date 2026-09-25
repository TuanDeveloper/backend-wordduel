from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ResponseSchema(BaseModel, Generic[T]):
    status: str = "success"
    data: T | None = None
    message: str = "Thao tác thành công"
    meta: dict[str, Any] | None = None

class ErrorResponseSchema(BaseModel):
    status: str = "error"
    error_code: str
    message: str
    details: Any | None = None
