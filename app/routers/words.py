from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.services import word_service
from app.schemas.word import WordSetResponse

router = APIRouter()


@router.get("/word-sets", response_model=List[WordSetResponse])
def get_word_sets(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Lấy danh sách các bộ từ vựng (Word Sets).
    """
    word_sets = word_service.get_word_sets(db, skip=skip, limit=limit)
    return word_sets


@router.get("/word-sets/{word_set_id}", response_model=WordSetResponse)
def get_word_set(
    word_set_id: int,
    db: Session = Depends(get_db),
):
    """
    Lấy chi tiết một bộ từ vựng theo ID.
    """
    word_set = word_service.get_word_set_by_id(db, word_set_id=word_set_id)
    if not word_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word set not found",
        )
    return word_set
