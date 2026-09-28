from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr = Field(max_length=254)
    full_name: str = Field(min_length=1, max_length=100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()

    @field_validator("full_name")
    @classmethod
    def full_name_is_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Họ và tên không được để trống")
        return cleaned


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Mật khẩu không được vượt quá 72 byte")
        return value

class UserLogin(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=72)

    @field_validator("password")
    @classmethod
    def login_password_fits_bcrypt(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Mật khẩu không được vượt quá 72 byte")
        return value

class UserResponse(UserBase):
    id: int
    created_at: datetime
    role: str = "user"
    avatar_key: str = "spark"
    preferences: dict = Field(default_factory=dict)
    rating: int = 1000
    rated_games: int = 0
    wins: int = 0

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ProfileUpdate(BaseModel):
    avatar_key: str | None = Field(default=None, pattern=r"^(spark|fox|owl|cat|dragon|robot|rocket|star)$")
    avatar_image: str | None = Field(default=None, max_length=700_000)
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    preferences: dict | None = None

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên hiển thị không được để trống")
        return cleaned

    @field_validator("avatar_image")
    @classmethod
    def validate_avatar_image(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return value
        import base64
        import re

        match = re.fullmatch(r"data:image/(?:png|jpeg|webp);base64,([A-Za-z0-9+/]+={0,2})", value)
        if not match:
            raise ValueError("Ảnh đại diện phải là PNG, JPEG hoặc WebP hợp lệ")
        try:
            image_bytes = base64.b64decode(match.group(1), validate=True)
        except ValueError as exc:
            raise ValueError("Dữ liệu ảnh không hợp lệ") from exc
        if not image_bytes or len(image_bytes) > 512_000:
            raise ValueError("Ảnh đại diện không được vượt quá 500 KB")
        return value

    @field_validator("preferences")
    @classmethod
    def validate_preferences(cls, value: dict | None) -> dict | None:
        if value is None:
            return value
        allowed = {"theme", "accent", "locale", "backgroundMusic", "soundEffects", "voice", "speechRate"}
        if set(value) - allowed:
            raise ValueError("Cài đặt có trường không được hỗ trợ")
        if not isinstance(value.get("theme", "dark"), str) or value.get("theme", "dark") not in {"dark", "light"}:
            raise ValueError("Giao diện không hợp lệ")
        if not isinstance(value.get("accent", "violet"), str) or value.get("accent", "violet") not in {"violet", "teal", "rose"}:
            raise ValueError("Màu nhấn không hợp lệ")
        if not isinstance(value.get("locale", "vi"), str) or value.get("locale", "vi") not in {"vi", "en"}:
            raise ValueError("Ngôn ngữ không hợp lệ")
        if not isinstance(value.get("voice", "en-US"), str) or value.get("voice", "en-US") not in {"en-US", "en-GB"}:
            raise ValueError("Giọng đọc không hợp lệ")
        if isinstance(value.get("speechRate", 1), bool) or not isinstance(value.get("speechRate", 1), (int, float)) or value.get("speechRate", 1) not in {0.75, 1}:
            raise ValueError("Tốc độ đọc không hợp lệ")
        for key in ("backgroundMusic", "soundEffects"):
            if key in value and not isinstance(value[key], bool):
                raise ValueError(f"{key} phải là true hoặc false")
        return value

