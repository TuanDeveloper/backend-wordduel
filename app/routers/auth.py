import json
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, UnauthorizedError
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.response import ResponseSchema
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import (
    authenticate_user,
    create_user,
    login_for_access_token,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=ResponseSchema[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
) -> ResponseSchema[UserResponse]:
    db_user = create_user(db, user)
    return ResponseSchema(data=db_user, message="Đăng ký tài khoản thành công")


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)) -> dict:
    """Accept OAuth2 form data from Swagger and JSON credentials from the UI."""
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
            if not isinstance(body_json, dict):
                raise ValueError("Expected a JSON object")
            username = body_json.get("username")
            password = body_json.get("password")
        except (json.JSONDecodeError, ValueError):
            parsed = parse_qs(raw_body.decode("utf-8", errors="replace"))
            username = parsed.get("username", [None])[0]
            password = parsed.get("password", [None])[0]

    try:
        credentials = UserLogin.model_validate({"username": username, "password": password})
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc

    db_user = authenticate_user(
        db, username=credentials.username.strip(), password=credentials.password
    )
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
