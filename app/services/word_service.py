from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.word import WordSet, Word
from app.schemas.word import WordSetCreate, WordSetUpdate, WordCreate, WordUpdate
from app.core.exceptions import NotFoundError, ForbiddenError


def get_word_sets(db: Session, skip: int = 0, limit: int = 100) -> List[WordSet]:
    """Lấy danh sách các bộ từ vựng"""
    return db.query(WordSet).offset(skip).limit(limit).all()


def get_word_set_by_id(db: Session, word_set_id: int) -> Optional[WordSet]:
    """Lấy chi tiết một bộ từ vựng theo ID"""
    return db.query(WordSet).filter(WordSet.id == word_set_id).first()


def get_words_by_set_id(db: Session, word_set_id: int, skip: int = 0, limit: int = 100) -> List[Word]:
    """Lấy danh sách từ vựng thuộc về một word set"""
    return db.query(Word).filter(Word.word_set_id == word_set_id).offset(skip).limit(limit).all()


def create_word_set(db: Session, word_set_in: WordSetCreate, creator_id: int) -> WordSet:
    """Tạo một bộ từ vựng mới kèm danh sách từ nếu có"""
    db_word_set = WordSet(
        title=word_set_in.title,
        description=word_set_in.description,
        creator_id=creator_id,
    )
    if word_set_in.words:
        for w in word_set_in.words:
            db_word = Word(
                term=w.term,
                definition=w.definition,
                example=w.example,
            )
            db_word_set.words.append(db_word)

    db.add(db_word_set)
    db.commit()
    db.refresh(db_word_set)
    return db_word_set


def update_word_set(
    db: Session, word_set_id: int, word_set_in: WordSetUpdate, user_id: int
) -> WordSet:
    """Cập nhật thông tin bộ từ vựng (chỉ chủ sở hữu mới có quyền)"""
    db_word_set = get_word_set_by_id(db, word_set_id)
    if not db_word_set:
        raise NotFoundError("Không tìm thấy bộ từ vựng")
    if db_word_set.creator_id != user_id:
        raise ForbiddenError("Bạn không có quyền sửa bộ từ vựng này")

    if word_set_in.title is not None:
        db_word_set.title = word_set_in.title
    if word_set_in.description is not None:
        db_word_set.description = word_set_in.description

    db.commit()
    db.refresh(db_word_set)
    return db_word_set


def delete_word_set(db: Session, word_set_id: int, user_id: int) -> None:
    """Xóa bộ từ vựng (chỉ chủ sở hữu mới có quyền)"""
    db_word_set = get_word_set_by_id(db, word_set_id)
    if not db_word_set:
        raise NotFoundError("Không tìm thấy bộ từ vựng")
    if db_word_set.creator_id != user_id:
        raise ForbiddenError("Bạn không có quyền xóa bộ từ vựng này")

    db.delete(db_word_set)
    db.commit()


def create_word(db: Session, word_set_id: int, word_in: WordCreate, user_id: int) -> Word:
    """Thêm một từ vựng vào bộ từ (chỉ chủ sở hữu mới có quyền)"""
    db_word_set = get_word_set_by_id(db, word_set_id)
    if not db_word_set:
        raise NotFoundError("Không tìm thấy bộ từ vựng")
    if db_word_set.creator_id != user_id:
        raise ForbiddenError("Bạn không có quyền thêm từ vào bộ từ vựng này")

    db_word = Word(
        word_set_id=word_set_id,
        term=word_in.term,
        definition=word_in.definition,
        example=word_in.example,
    )
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word


def update_word(db: Session, word_id: int, word_in: WordUpdate, user_id: int) -> Word:
    """Cập nhật một từ vựng (chỉ chủ sở hữu bộ từ mới có quyền)"""
    db_word = db.query(Word).filter(Word.id == word_id).first()
    if not db_word:
        raise NotFoundError("Không tìm thấy từ vựng")

    db_word_set = get_word_set_by_id(db, db_word.word_set_id)
    if not db_word_set or db_word_set.creator_id != user_id:
        raise ForbiddenError("Bạn không có quyền chỉnh sửa từ vựng này")

    if word_in.term is not None:
        db_word.term = word_in.term
    if word_in.definition is not None:
        db_word.definition = word_in.definition
    if word_in.example is not None:
        db_word.example = word_in.example

    db.commit()
    db.refresh(db_word)
    return db_word


def delete_word(db: Session, word_id: int, user_id: int) -> None:
    """Xóa một từ vựng (chỉ chủ sở hữu bộ từ mới có quyền)"""
    db_word = db.query(Word).filter(Word.id == word_id).first()
    if not db_word:
        raise NotFoundError("Không tìm thấy từ vựng")

    db_word_set = get_word_set_by_id(db, db_word.word_set_id)
    if not db_word_set or db_word_set.creator_id != user_id:
        raise ForbiddenError("Bạn không có quyền xóa từ vựng này")

    db.delete(db_word)
    db.commit()

