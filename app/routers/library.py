from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ConflictError, NotFoundError
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.learning import SavedWord
from app.models.user import User
from app.models.word import Word, WordSet
from app.schemas.response import ResponseSchema
from app.schemas.learning import SaveWordRequest

router = APIRouter(prefix="/library", tags=["library"])


@router.post("/save", response_model=ResponseSchema[dict], status_code=status.HTTP_201_CREATED)
def save_word(
    payload: SaveWordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    word_id = payload.word_id
    note = payload.note
    word = db.query(Word).options(joinedload(Word.word_set)).filter(Word.id == word_id).first()
    if not word:
        raise NotFoundError("Không tìm thấy từ vựng")
    existing = db.query(SavedWord).filter(
        SavedWord.user_id == current_user.id, SavedWord.word_id == word_id
    ).first()
    if existing:
        return ResponseSchema(data=_saved_word_payload(existing, word), message="Từ này đã có trong thư viện")
    saved = SavedWord(user_id=current_user.id, word_id=word_id, note=note)
    db.add(saved)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        existing = db.query(SavedWord).filter(
            SavedWord.user_id == current_user.id, SavedWord.word_id == word_id
        ).first()
        if existing:
            return ResponseSchema(data=_saved_word_payload(existing, word), message="Từ này đã có trong thư viện")
        raise ConflictError("Không thể lưu từ vựng") from exc
    db.refresh(saved)
    return ResponseSchema(data=_saved_word_payload(saved, word), message="Đã lưu từ vào thư viện")


def _saved_word_payload(saved: SavedWord, word: Word) -> dict:
    return {
        "id": saved.id,
        "word_id": word.id,
        "note": saved.note,
        "created_at": saved.created_at or datetime.utcnow(),
        "word": {
            "id": word.id,
            "word_set_id": word.word_set_id,
            "term": word.term,
            "definition": word.definition,
            "example": word.example,
            "context_sentence": word.context_sentence,
        },
    }


@router.get("", response_model=ResponseSchema[list[dict]])
def list_saved_words(
    search: str | None = Query(default=None, max_length=100),
    skip: int = Query(default=0, ge=0, le=1_000_000),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[list[dict]]:
    query = (
        db.query(SavedWord)
        .join(Word, SavedWord.word_id == Word.id)
        .join(WordSet, WordSet.id == Word.word_set_id)
        .options(joinedload(SavedWord.word))
        .filter(SavedWord.user_id == current_user.id, WordSet.is_hidden.is_(False))
    )
    if search and search.strip():
        needle = f"%{search.strip()}%"
        query = query.filter(or_(
            Word.term.ilike(needle),
            Word.definition.ilike(needle),
            Word.example.ilike(needle),
            Word.context_sentence.ilike(needle),
        ))
    entries = query.order_by(SavedWord.created_at.desc()).offset(skip).limit(limit).all()
    return ResponseSchema(data=[_saved_word_payload(entry, entry.word) for entry in entries], message="Thư viện cá nhân")


@router.delete("/{saved_word_id}", response_model=ResponseSchema[None])
def remove_saved_word(
    saved_word_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[None]:
    entry = db.query(SavedWord).filter(
        SavedWord.id == saved_word_id, SavedWord.user_id == current_user.id
    ).first()
    if not entry:
        raise NotFoundError("Không tìm thấy từ trong thư viện")
    db.delete(entry)
    db.commit()
    return ResponseSchema(data=None, message="Đã bỏ lưu từ")
