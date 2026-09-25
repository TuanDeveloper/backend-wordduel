import json
from urllib.parse import parse_qs
from fastapi import APIRouter, Depends, status, Request
from app.core.exceptions import UnauthorizedError, BadRequestError
from app.schemas.response import ResponseSchema
from app.services.auth_service import authenticate_user
from app.schemas.user import TokenResponse
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.services.auth_service import create_user, login_for_access_token
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()

# Viết các API Authentication ở đây (POST /register, POST /login, ...)
@router.post("/register", response_model=ResponseSchema[UserResponse], status_code=status.HTTP_201_CREATED)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
) -> ResponseSchema[UserResponse]:
    db_user = create_user(db, user) 
    return ResponseSchema(data=db_user, message="Đăng ký tài khoản thành công")

@router.post("/login")
async def login(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Đăng nhập: Hỗ trợ cả Form-data (Swagger UI Authorize) và JSON body (Frontend).
    Trả về access_token ở root (chuẩn OAuth2 cho Swagger) và bọc data (chuẩn ResponseSchema cho Frontend).
    """
    content_type = request.headers.get("content-type", "").lower()
    raw_body = await request.body()
    username = None
    password = None

    if "application/x-www-form-urlencoded" in content_type:
        parsed = parse_qs(raw_body.decode("utf-8", errors="replace"))
        username = parsed.get("username", [None])[0]
        password = parsed.get("password", [None])[0]
    else:
        try:
            body_json = json.loads(raw_body.decode("utf-8", errors="replace"))
            username = body_json.get("username")
            password = body_json.get("password")
        except Exception:
            parsed = parse_qs(raw_body.decode("utf-8", errors="replace"))
            username = parsed.get("username", [None])[0]
            password = parsed.get("password", [None])[0]

    if not username or not password:
        raise BadRequestError(message="Vui lòng nhập tên đăng nhập và mật khẩu")

    db_user = authenticate_user(db, username=str(username).strip(), password=str(password))
    if not db_user:
        raise UnauthorizedError(message="Sai tên đăng nhập hoặc mật khẩu")

    token_data = login_for_access_token(db_user)
    return {
        "access_token": token_data.access_token,
        "token_type": token_data.token_type,
        "status": "success",
        "message": "Đăng nhập thành công",
        "data": {
            "access_token": token_data.access_token,
            "token_type": token_data.token_type,
        },
    }


@router.get("/me", response_model=ResponseSchema[UserResponse])
def get_me(
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[UserResponse]:
    return ResponseSchema(data=current_user, message="Lấy thông tin người dùng thành công")


