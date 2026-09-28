from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import cast, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.core.security import hash_password
from app.dependencies.auth import require_admin
from app.dependencies.database import get_db
from app.models.room import Room, RoomPlayer, Submission
from app.models.user import User
from app.models.word import Word, WordSet
from app.schemas.word import WordCreate, WordSetCreate, WordSetUpdate, WordUpdate
from app.schemas.response import ResponseSchema
from app.websockets.connection_manager import manager

router = APIRouter(prefix="/admin", tags=["admin"])


class AccountStatusUpdate(BaseModel):
    is_active: bool


class WordSetModerationUpdate(BaseModel):
    is_hidden: bool


class AdminUserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=72)
    role: str = Field(default="user", pattern=r"^(user|admin)$")

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Mật khẩu không được vượt quá 72 byte")
        return value

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Họ tên không được để trống")
        return value


class AdminUserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    role: str | None = Field(default=None, pattern=r"^(user|admin)$")


def _user_data(user: User) -> dict:
    return {"id": user.id, "username": user.username, "email": user.email,
            "full_name": user.full_name, "role": user.role, "is_active": user.is_active,
            "created_at": user.created_at}


def _get_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("Không tìm thấy tài khoản")
    return user


@router.get("/users", response_model=ResponseSchema[list[dict]])
def list_users(
    search: str | None = Query(default=None, max_length=100),
    skip: int = Query(default=0, ge=0, le=1_000_000),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ResponseSchema[list[dict]]:
    query = db.query(User)
    if search and search.strip():
        needle = f"%{search.strip()}%"
        query = query.filter((User.username.ilike(needle)) | (User.email.ilike(needle)) | (User.full_name.ilike(needle)))
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return ResponseSchema(data=[
        {
            **_user_data(user),
        }
        for user in users
    ], message="Danh sách tài khoản")


@router.post("/users", response_model=ResponseSchema[dict], status_code=status.HTTP_201_CREATED)
def create_user(payload: AdminUserCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    email = str(payload.email).lower()
    if db.query(User.id).filter(or_(User.username == payload.username, func.lower(User.email) == email)).first():
        raise ConflictError("Tên đăng nhập hoặc email đã tồn tại")
    user = User(username=payload.username, email=email, full_name=payload.full_name.strip(),
                password_hash=hash_password(payload.password), role=payload.role)
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Tên đăng nhập hoặc email đã tồn tại") from exc
    db.refresh(user)
    return ResponseSchema(data=_user_data(user), message="Đã tạo tài khoản")


@router.put("/users/{user_id}", response_model=ResponseSchema[dict])
def update_user(user_id: int, payload: AdminUserUpdate, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    target = _get_user(db, user_id)
    changes = payload.model_dump(exclude_unset=True)
    if any(value is None for value in changes.values()):
        raise BadRequestError("Thông tin cập nhật không được để trống")
    if target.id == admin_user.id and changes.get("role") == "user":
        raise BadRequestError("Không thể tự hạ quyền admin của tài khoản đang đăng nhập")
    if "username" in changes:
        duplicate = db.query(User.id).filter(User.username == changes["username"], User.id != user_id).first()
        if duplicate:
            raise ConflictError("Tên đăng nhập đã được sử dụng")
        target.username = changes["username"]
    if "email" in changes:
        email = str(changes["email"]).lower()
        duplicate = db.query(User.id).filter(func.lower(User.email) == email, User.id != user_id).first()
        if duplicate:
            raise ConflictError("Email đã được sử dụng")
        target.email = email
    if "full_name" in changes:
        target.full_name = changes["full_name"].strip()
        if not target.full_name:
            raise BadRequestError("Họ tên không được để trống")
    if "role" in changes:
        target.role = changes["role"]
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Tên đăng nhập hoặc email đã được sử dụng") from exc
    db.refresh(target)
    return ResponseSchema(data=_user_data(target), message="Đã cập nhật tài khoản")


@router.delete("/users/{user_id}", response_model=ResponseSchema[dict])
def delete_user(user_id: int, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    target = _get_user(db, user_id)
    if target.id == admin_user.id:
        raise BadRequestError("Không thể xóa tài khoản admin đang đăng nhập")
    if target.role == "admin" and db.query(User.id).filter(User.role == "admin", User.id != user_id).first() is None:
        raise BadRequestError("Không thể xóa admin cuối cùng của hệ thống")
    has_room_history = db.query(Room.id).filter(Room.host_id == user_id).first() or db.query(RoomPlayer.id).filter(RoomPlayer.user_id == user_id).first() or db.query(Submission.id).filter(Submission.user_id == user_id).first()
    if has_room_history:
        raise BadRequestError("Tài khoản đã có lịch sử trận đấu; hãy khóa tài khoản thay vì xóa để bảo toàn dữ liệu")
    db.query(WordSet).filter(WordSet.creator_id == user_id).update({WordSet.creator_id: None}, synchronize_session=False)
    db.delete(target)
    db.commit()
    return ResponseSchema(data={"id": user_id}, message="Đã xóa tài khoản")


@router.patch("/users/{user_id}/status", response_model=ResponseSchema[dict])
def set_user_status(
    user_id: int,
    update: AccountStatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> ResponseSchema[dict]:
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise NotFoundError("Không tìm thấy tài khoản")
    if target.id == admin_user.id and not update.is_active:
        from app.core.exceptions import BadRequestError
        raise BadRequestError("Không thể khóa tài khoản admin đang đăng nhập")
    if target.role == "admin" and not update.is_active and db.query(User.id).filter(User.role == "admin", User.is_active.is_(True), User.id != user_id).first() is None:
        raise BadRequestError("Không thể khóa admin hoạt động cuối cùng của hệ thống")
    target.is_active = update.is_active
    db.commit()
    return ResponseSchema(data={"id": target.id, "is_active": target.is_active}, message="Cập nhật trạng thái tài khoản")


@router.get("/word-sets", response_model=ResponseSchema[list[dict]])
def list_all_word_sets(
    search: str | None = Query(default=None, max_length=100),
    skip: int = Query(default=0, ge=0, le=1_000_000),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ResponseSchema[list[dict]]:
    query = (
        db.query(WordSet, User.username, func.count(Word.id).label("word_count"))
        .outerjoin(User, User.id == WordSet.creator_id)
        .outerjoin(Word, Word.word_set_id == WordSet.id)
        .group_by(WordSet.id, User.username)
    )
    if search and search.strip():
        needle = f"%{search.strip()}%"
        query = query.filter(or_(WordSet.title.ilike(needle), WordSet.description.ilike(needle), User.username.ilike(needle)))
    rows = query.order_by(WordSet.id.desc()).offset(skip).limit(limit).all()
    return ResponseSchema(data=[
        {
            "id": word_set.id,
            "title": word_set.title,
            "description": word_set.description,
            "creator_id": word_set.creator_id,
            "creator_username": creator,
            "word_count": word_count,
            "is_hidden": word_set.is_hidden,
        }
        for word_set, creator, word_count in rows
    ], message="Quản lý bộ từ vựng")


@router.get("/word-sets/{word_set_id}", response_model=ResponseSchema[dict])
def get_word_set_for_review(
    word_set_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ResponseSchema[dict]:
    word_set = db.query(WordSet).filter(WordSet.id == word_set_id).first()
    if not word_set:
        raise NotFoundError("Không tìm thấy bộ từ vựng")
    words = db.query(Word).filter(Word.word_set_id == word_set.id).order_by(Word.id).limit(500).all()
    return ResponseSchema(data={
        "id": word_set.id,
        "title": word_set.title,
        "description": word_set.description,
        "creator_id": word_set.creator_id,
        "is_hidden": word_set.is_hidden,
        "words": [
            {
                "id": word.id,
                "term": word.term,
                "definition": word.definition,
                "example": word.example,
                "context_sentence": word.context_sentence,
            }
            for word in words
        ],
    }, message="Nội dung bộ từ để kiểm duyệt")


@router.patch("/word-sets/{word_set_id}", response_model=ResponseSchema[dict])
def moderate_word_set(
    word_set_id: int,
    update: WordSetModerationUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ResponseSchema[dict]:
    word_set = db.query(WordSet).filter(WordSet.id == word_set_id).first()
    if not word_set:
        raise NotFoundError("Không tìm thấy bộ từ vựng")
    word_set.is_hidden = update.is_hidden
    db.commit()
    return ResponseSchema(data={"id": word_set.id, "is_hidden": word_set.is_hidden}, message="Cập nhật kiểm duyệt")


@router.post("/word-sets", response_model=ResponseSchema[dict], status_code=status.HTTP_201_CREATED)
def create_admin_word_set(payload: WordSetCreate, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    title = payload.title.strip()
    if not title:
        raise BadRequestError("Tên bộ từ không được để trống")
    word_set = WordSet(title=title, description=payload.description, creator_id=admin_user.id)
    word_set.words = [Word(term=item.term, definition=item.definition, example=item.example,
                           context_sentence=item.context_sentence) for item in payload.words]
    db.add(word_set)
    db.commit()
    db.refresh(word_set)
    return ResponseSchema(data={"id": word_set.id, "title": word_set.title, "description": word_set.description,
                                "creator_id": word_set.creator_id, "is_hidden": word_set.is_hidden,
                                "word_count": len(word_set.words)}, message="Đã tạo bộ từ")


@router.put("/word-sets/{word_set_id}", response_model=ResponseSchema[dict])
def update_admin_word_set(word_set_id: int, payload: WordSetUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    word_set = db.query(WordSet).filter(WordSet.id == word_set_id).first()
    if not word_set:
        raise NotFoundError("Không tìm thấy bộ từ vựng")
    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise BadRequestError("Tên bộ từ không được để trống")
        word_set.title = title
    if payload.description is not None:
        word_set.description = payload.description
    db.commit()
    return ResponseSchema(data={"id": word_set.id, "title": word_set.title, "description": word_set.description}, message="Đã cập nhật bộ từ")


@router.delete("/word-sets/{word_set_id}", response_model=ResponseSchema[dict])
def delete_admin_word_set(word_set_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    word_set = db.query(WordSet).filter(WordSet.id == word_set_id).first()
    if not word_set:
        raise NotFoundError("Không tìm thấy bộ từ vựng")
    linked_rooms = (db.query(Room)
        .filter(or_(
            Room.word_set_id == word_set_id,
            cast(Room.word_set_ids, JSONB).contains([word_set_id]),
        ))
        .with_for_update()
        .all())
    unfinished = [room for room in linked_rooms if room.status != "finished"]
    if unfinished:
        raise BadRequestError("Bộ từ đang được dùng trong phòng chưa kết thúc; hãy kết thúc hoặc đóng phòng trước khi xóa")

    # Finished rooms and their player scores/submissions are part of the
    # explicitly requested deletion. Room ORM cascades remove those child rows.
    for room in linked_rooms:
        db.delete(room)
    db.flush()
    db.delete(word_set)
    db.commit()
    return ResponseSchema(data={"id": word_set_id, "deleted_finished_rooms": len(linked_rooms)}, message="Đã xóa bộ từ và các trận đã kết thúc sử dụng bộ từ này")


@router.get("/rooms", response_model=ResponseSchema[list[dict]])
def list_unfinished_rooms(
    search: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = (db.query(Room, User.username, WordSet.title, func.count(RoomPlayer.id).label("player_count"))
        .join(User, User.id == Room.host_id)
        .outerjoin(WordSet, WordSet.id == Room.word_set_id)
        .outerjoin(RoomPlayer, RoomPlayer.room_id == Room.id)
        .filter(Room.status.in_(["waiting", "playing"]))
        .group_by(Room.id, User.username, WordSet.title))
    if search and search.strip():
        needle = f"%{search.strip()}%"
        query = query.filter(or_(Room.code.ilike(needle), User.username.ilike(needle), WordSet.title.ilike(needle)))
    rows = query.order_by(Room.created_at.desc()).limit(200).all()
    return ResponseSchema(data=[
        {"id": room.id, "code": room.code, "status": room.status, "host_username": host,
         "word_set_title": title or "(bộ từ đã bị xóa)", "player_count": player_count,
         "created_at": room.created_at}
        for room, host, title, player_count in rows
    ], message="Danh sách phòng chưa kết thúc")


@router.post("/rooms/{room_id}/reconcile", response_model=ResponseSchema[dict])
async def finish_abandoned_room(room_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    room = db.query(Room).filter(Room.id == room_id).with_for_update().first()
    if not room:
        raise NotFoundError("Không tìm thấy phòng")
    if room.status not in ("waiting", "playing"):
        raise BadRequestError("Phòng này không còn ở trạng thái hoạt động")
    players = db.query(RoomPlayer).filter(RoomPlayer.room_id == room.id).all()
    if len(players) >= 2:
        raise BadRequestError("Phòng vẫn còn đủ người chơi; không thể tự động kết thúc")

    # Legacy rooms may have been left active after participants exited.
    # Preserve remaining rows, but do not award ELO without a complete match.
    from datetime import datetime
    from app.services.game_service import _finish_payload

    was_waiting = room.status == "waiting"
    room.status = "finished"
    room.finished_at = datetime.utcnow()
    db.commit()
    room = (db.query(Room)
        .filter(Room.id == room_id)
        .first())
    if was_waiting:
        await manager.broadcast(room.code, {"event": "room_closed", "reason": "admin_closed", "players": []})
    else:
        payload = _finish_payload(room, db)
        if room.board_game_mode:
            payload["board_game_mode"] = room.board_game_mode
        await manager.broadcast(room.code, payload)
    return ResponseSchema(data={"id": room.id, "code": room.code, "status": room.status}, message="Đã đóng phòng chưa đủ người; ELO không thay đổi")


@router.post("/word-sets/{word_set_id}/words", response_model=ResponseSchema[dict], status_code=status.HTTP_201_CREATED)
def add_admin_word(word_set_id: int, payload: WordCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    word_set = db.query(WordSet).filter(WordSet.id == word_set_id).first()
    if not word_set:
        raise NotFoundError("Không tìm thấy bộ từ vựng")
    word = Word(word_set_id=word_set_id, **payload.model_dump())
    db.add(word)
    db.commit()
    db.refresh(word)
    return ResponseSchema(data={"id": word.id, "term": word.term, "definition": word.definition,
                                "example": word.example, "context_sentence": word.context_sentence}, message="Đã thêm từ")


@router.put("/word-sets/{word_set_id}/words/{word_id}", response_model=ResponseSchema[dict])
def update_admin_word(word_set_id: int, word_id: int, payload: WordUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    word = db.query(Word).filter(Word.id == word_id, Word.word_set_id == word_set_id).first()
    if not word:
        raise NotFoundError("Không tìm thấy từ trong bộ từ này")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(word, field, value)
    db.commit()
    return ResponseSchema(data={"id": word.id, "term": word.term, "definition": word.definition,
                                "example": word.example, "context_sentence": word.context_sentence}, message="Đã cập nhật từ")


@router.delete("/word-sets/{word_set_id}/words/{word_id}", response_model=ResponseSchema[dict])
def delete_admin_word(word_set_id: int, word_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    word = db.query(Word).filter(Word.id == word_id, Word.word_set_id == word_set_id).first()
    if not word:
        raise NotFoundError("Không tìm thấy từ trong bộ từ này")
    if db.query(Submission.id).filter(Submission.word_id == word_id).first():
        raise BadRequestError("Từ đã xuất hiện trong lịch sử trận; không thể xóa để bảo toàn kết quả")
    db.delete(word)
    db.commit()
    return ResponseSchema(data={"id": word_id}, message="Đã xóa từ")


@router.get("/stats", response_model=ResponseSchema[dict])
def get_admin_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ResponseSchema[dict]:
    popular_sets = (
        db.query(WordSet.id, WordSet.title, func.count(Room.id).label("room_count"))
        .outerjoin(Room, Room.word_set_id == WordSet.id)
        .group_by(WordSet.id)
        .order_by(func.count(Room.id).desc(), WordSet.title.asc())
        .limit(10)
        .all()
    )
    data = {
        "user_count": db.query(func.count(User.id)).scalar() or 0,
        "active_user_count": db.query(func.count(User.id)).filter(User.is_active.is_(True)).scalar() or 0,
        "finished_room_count": db.query(func.count(Room.id)).filter(Room.status == "finished").scalar() or 0,
        "word_set_count": db.query(func.count(WordSet.id)).scalar() or 0,
        "popular_word_sets": [
            {"id": row.id, "title": row.title, "room_count": row.room_count}
            for row in popular_sets
        ],
    }
    return ResponseSchema(data=data, message="Thống kê hệ thống")
