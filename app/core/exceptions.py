from fastapi import HTTPException, status

class BaseAPIException(HTTPException):
    def __init__(self, status_code: int, error_code: str, message: str, details: any = None):
        super().__init__(status_code=status_code, detail=message)
        self.error_code = error_code
        self.message = message
        self.details = details

class BadRequestError(BaseAPIException):
    def __init__(self, message: str = "Dữ liệu đầu vào không hợp lệ", details: any = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BAD_REQUEST",
            message=message,
            details=details,
        )

class UnauthorizedError(BaseAPIException):
    def __init__(self, message: str = "Không có quyền truy cập hoặc xác thực thất bại"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            message=message,
        )

class ForbiddenError(BaseAPIException):
    def __init__(self, message: str = "Bạn không có quyền thực hiện hành động này"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
            message=message,
        )

class NotFoundError(BaseAPIException):
    def __init__(self, message: str = "Không tìm thấy tài nguyên yêu cầu"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=message,
        )

class ConflictError(BaseAPIException):
    def __init__(self, message: str = "Tài nguyên đã tồn tại hoặc xảy ra xung đột"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message=message,
        )

class InternalServerError(BaseAPIException):
    def __init__(self, message: str = "Lỗi hệ thống", details: any = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR",
            message=message,
            details=details,
        )
