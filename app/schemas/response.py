from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class ResponseSchema(BaseModel, Generic[T]):
    status: str = "success"
    data: Optional[T] = None
    message: str = "Thao tác thành công"
    meta: Optional[dict[str, Any]] = None

class ErrorResponseSchema(BaseModel):
    status: str = "error"
    error_code: str
    message: str
    details: Optional[Any] = None
