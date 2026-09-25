# Logic nghiệp vụ xác thực (Register, Login, Password Hashing, JWT generation)
# Sẽ được bạn viết tiếp khi làm phần Auth API
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate


def create_user(db: Session, user: UserCreate) -> User:
    existing_user = (
        db.query(User)
        .filter(or_(User.username == user.username, func.lower(User.email) == user.email.lower()))
        .first()
    )
    if existing_user:
        raise ConflictError(message="Tên đăng nhập hoặc email đã tồn tại")

    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        password_hash=hashed_password,
    )
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(message="Tên đăng nhập hoặc email đã tồn tại") from exc
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def login_for_access_token(user: User) -> TokenResponse:
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token, token_type="bearer")
