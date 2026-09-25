from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services import word_service
from app.schemas.word import (
    WordSetCreate,
    WordSetUpdate,
    WordSetResponse,
    WordCreate,
    WordUpdate,
    WordResponse,
)
from app.schemas.response import ResponseSchema
from app.core.exceptions import NotFoundError

router = APIRouter()


@router.get("/word-sets", response_model=ResponseSchema[List[WordSetResponse]])
@router.get("/words/sets", response_model=ResponseSchema[List[WordSetResponse]])
def get_word_sets(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> ResponseSchema[List[WordSetResponse]]:
    """Lấy danh sách các bộ từ vựng."""
    word_sets = word_service.get_word_sets(db, skip=skip, limit=limit)
    return ResponseSchema(data=word_sets, message="Lấy danh sách bộ từ vựng thành công")


@router.get("/word-sets/{word_set_id}", response_model=ResponseSchema[WordSetResponse])
@router.get("/words/sets/{word_set_id}", response_model=ResponseSchema[WordSetResponse])
def get_word_set(
    word_set_id: int,
    db: Session = Depends(get_db),
) -> ResponseSchema[WordSetResponse]:
    """Lấy chi tiết một bộ từ vựng theo ID."""
    word_set = word_service.get_word_set_by_id(db, word_set_id=word_set_id)
    if not word_set:
        raise NotFoundError(message="Không tìm thấy bộ từ vựng")
    return ResponseSchema(data=word_set, message="Lấy chi tiết bộ từ vựng thành công")


@router.post("/word-sets", response_model=ResponseSchema[WordSetResponse], status_code=status.HTTP_201_CREATED)
@router.post("/words/sets", response_model=ResponseSchema[WordSetResponse], status_code=status.HTTP_201_CREATED)
def create_word_set(
    word_set_in: WordSetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[WordSetResponse]:
    """Tạo một bộ từ vựng mới (kèm danh sách từ nếu có)."""
    db_word_set = word_service.create_word_set(db, word_set_in=word_set_in, creator_id=current_user.id)
    return ResponseSchema(data=db_word_set, message="Tạo bộ từ vựng thành công")


@router.put("/word-sets/{word_set_id}", response_model=ResponseSchema[WordSetResponse])
@router.put("/words/sets/{word_set_id}", response_model=ResponseSchema[WordSetResponse])
def update_word_set(
    word_set_id: int,
    word_set_in: WordSetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[WordSetResponse]:
    """Cập nhật bộ từ vựng (chỉ chủ sở hữu)."""
    db_word_set = word_service.update_word_set(
        db, word_set_id=word_set_id, word_set_in=word_set_in, user_id=current_user.id
    )
    return ResponseSchema(data=db_word_set, message="Cập nhật bộ từ vựng thành công")


@router.delete("/word-sets/{word_set_id}", response_model=ResponseSchema[None])
@router.delete("/words/sets/{word_set_id}", response_model=ResponseSchema[None])
def delete_word_set(
    word_set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[None]:
    """Xóa bộ từ vựng (chỉ chủ sở hữu)."""
    word_service.delete_word_set(db, word_set_id=word_set_id, user_id=current_user.id)
    return ResponseSchema(data=None, message="Xóa bộ từ vựng thành công")



@router.post(
    "/word-sets/{word_set_id}/words",
    response_model=ResponseSchema[WordResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_word(
    word_set_id: int,
    word_in: WordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[WordResponse]:
    """Thêm một từ vựng vào bộ từ (chỉ chủ sở hữu bộ từ)."""
    db_word = word_service.create_word(
        db, word_set_id=word_set_id, word_in=word_in, user_id=current_user.id
    )
    return ResponseSchema(data=db_word, message="Thêm từ vựng thành công")


@router.put("/words/{word_id}", response_model=ResponseSchema[WordResponse])
def update_word(
    word_id: int,
    word_in: WordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[WordResponse]:
    """Cập nhật từ vựng (chỉ chủ sở hữu bộ từ)."""
    db_word = word_service.update_word(
        db, word_id=word_id, word_in=word_in, user_id=current_user.id
    )
    return ResponseSchema(data=db_word, message="Cập nhật từ vựng thành công")


@router.delete("/words/{word_id}", response_model=ResponseSchema[None])
def delete_word(
    word_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[None]:
    """Xóa từ vựng (chỉ chủ sở hữu bộ từ)."""
    word_service.delete_word(db, word_id=word_id, user_id=current_user.id)
    return ResponseSchema(data=None, message="Xóa từ vựng thành công")

