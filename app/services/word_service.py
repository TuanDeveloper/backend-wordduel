from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.word import WordSet, Word


def get_word_sets(db: Session, skip: int = 0, limit: int = 100) -> List[WordSet]:
    """Lấy danh sách các bộ từ vựng"""
    return db.query(WordSet).offset(skip).limit(limit).all()


def get_word_set_by_id(db: Session, word_set_id: int) -> Optional[WordSet]:
    """Lấy chi tiết một bộ từ vựng theo ID"""
    return db.query(WordSet).filter(WordSet.id == word_set_id).first()


def get_words_by_set_id(db: Session, word_set_id: int, skip: int = 0, limit: int = 100) -> List[Word]:
    """Lấy danh sách từ vựng thuộc về một word set"""
    return db.query(Word).filter(Word.word_set_id == word_set_id).offset(skip).limit(limit).all()
