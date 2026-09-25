from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.dependencies.auth import require_admin
from app.dependencies.database import get_db
from app.models.room import Room
from app.models.user import User
from app.models.word import Word, WordSet
from app.schemas.response import ResponseSchema

router = APIRouter(prefix="/admin", tags=["admin"])


class AccountStatusUpdate(BaseModel):
    is_active: bool


class WordSetModerationUpdate(BaseModel):
    is_hidden: bool


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
        query = query.filter((User.username.ilike(needle)) | (User.email.ilike(needle)))
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return ResponseSchema(data=[
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
        }
        for user in users
    ], message="Danh sách tài khoản")


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
        query = query.filter(WordSet.title.ilike(f"%{search.strip()}%"))
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
