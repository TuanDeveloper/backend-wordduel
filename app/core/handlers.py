import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import BaseAPIException
from app.schemas.response import ErrorResponseSchema

logger = logging.getLogger(__name__)

def register_exception_handlers(app):

    @app.exception_handler(BaseAPIException)
    async def custom_exception_handler(request: Request, exc: BaseAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponseSchema(
                status="error",
                error_code=exc.error_code,
                message=exc.message,
                details=exc.details
            ).model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        details = []
        for err in errors:
            details.append({
                "loc": " -> ".join([str(x) for x in err.get("loc", [])]),
                "msg": err.get("msg"),
                "type": err.get("type")
            })

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponseSchema(
                status="error",
                error_code="VALIDATION_ERROR",
                message="Dữ liệu đầu vào không hợp lệ",
                details=details
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(
            "Unhandled request error: %s %s",
            request.method,
            request.url.path,
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponseSchema(
                status="error",
                error_code="INTERNAL_SERVER_ERROR",
                message="Đã xảy ra lỗi hệ thống không xác định",
                details=None,
            ).model_dump()
        )
