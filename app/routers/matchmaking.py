from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.response import ResponseSchema
from app.services import matchmaking_service

router = APIRouter(prefix="/matchmaking", tags=["matchmaking"])


class MatchmakingRequest(BaseModel):
    game_mode: Literal["classic", "reverse", "multiple_choice", "listen_choice", "listen_spelling", "fill_blank", "speak"]
    board_game_mode: Literal["monopoly", "boss", "race", "territory"] | None = None


@router.post("/search", response_model=ResponseSchema[dict])
def search(payload: MatchmakingRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    result = matchmaking_service.search(db, user.id, payload.game_mode, payload.board_game_mode)
    return ResponseSchema(data=result, message="Đã tham gia hàng chờ tìm trận")


@router.get("/status", response_model=ResponseSchema[dict])
def status(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ResponseSchema(data=matchmaking_service.status(db, user.id), message="Trạng thái tìm trận")


@router.delete("/search", response_model=ResponseSchema[dict])
def cancel(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ResponseSchema(data=matchmaking_service.cancel(db, user.id), message="Đã hủy tìm trận")
