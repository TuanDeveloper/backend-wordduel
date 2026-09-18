# Logic nghiệp vụ xác thực (Register, Login, Password Hashing, JWT generation)
# Sẽ được bạn viết tiếp khi làm phần Auth API
from app.schemas.user import TokenResponse
from app.core.security import verify_password
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password
from app.core.security import create_access_token   


from app.core.exceptions import ConflictError

def create_user(db: Session, user: UserCreate) -> User:
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
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
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> User:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

def login_for_access_token(user: User) -> TokenResponse:
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token, token_type="bearer")
