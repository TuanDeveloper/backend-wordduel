from app.core.exceptions import UnauthorizedError
from app.schemas.response import ResponseSchema
from app.services.auth_service import authenticate_user
from app.schemas.user import TokenResponse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.services.auth_service import create_user, login_for_access_token
from app.dependencies.database import get_db


router = APIRouter()

# Viết các API Authentication ở đây (POST /register, POST /login, ...)
@router.post("/register", response_model=ResponseSchema[UserResponse], status_code=status.HTTP_201_CREATED)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
) -> ResponseSchema[UserResponse]:
    db_user = create_user(db, user) 
    return ResponseSchema(data=db_user, message="Đăng ký tài khoản thành công")

@router.post("/login", response_model=ResponseSchema[TokenResponse])
def login(
    user: UserLogin,
    db: Session = Depends(get_db),
) -> ResponseSchema[TokenResponse]:
    # Bước 1: Kiểm tra username / password trong DB
    db_user = authenticate_user(db, username=user.username, password=user.password)
    if not db_user:
        raise UnauthorizedError(message="Sai tên đăng nhập hoặc mật khẩu")
    
    # Bước 2: Nếu đúng, tạo token
    token_data = login_for_access_token(db_user)
    return ResponseSchema(data=token_data, message="Đăng nhập thành công")

