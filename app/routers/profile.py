from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.models.room import Room, RoomPlayer
from app.schemas.response import ResponseSchema
from app.schemas.user import ProfileUpdate, UserResponse

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ResponseSchema[UserResponse])
def get_profile(current_user: User = Depends(get_current_user)) -> ResponseSchema[UserResponse]:
    return ResponseSchema(data=current_user, message="Đã tải hồ sơ")


@router.patch("", response_model=ResponseSchema[UserResponse])
def update_profile(
    request: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[UserResponse]:
    if request.avatar_key is not None:
        current_user.avatar_key = request.avatar_key
    if request.full_name is not None:
        current_user.full_name = request.full_name
    if request.avatar_image is not None:
        preferences = dict(current_user.preferences or {})
        if request.avatar_image:
            preferences["avatarImage"] = request.avatar_image
        else:
            preferences.pop("avatarImage", None)
        current_user.preferences = preferences
    if request.preferences is not None:
        current_user.preferences = {**(current_user.preferences or {}), **request.preferences}
    db.commit()
    db.refresh(current_user)
    return ResponseSchema(data=current_user, message="Đã lưu tùy chỉnh")


@router.get("/matches", response_model=ResponseSchema[list[dict]])
def get_match_history(
    limit: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[list[dict]]:
    limit = max(1, min(limit, 100))
    rooms = (
        db.query(Room)
        .options(joinedload(Room.players).joinedload(RoomPlayer.user))
        .join(RoomPlayer, RoomPlayer.room_id == Room.id)
        .filter(RoomPlayer.user_id == current_user.id, Room.status == "finished")
        .order_by(Room.finished_at.desc().nullslast(), Room.created_at.desc())
        .limit(limit)
        .all()
    )
    history = []
    for room in rooms:
        own = next((player for player in room.players if player.user_id == current_user.id), None)
        if own is None:
            continue
        others = [player for player in room.players if player.user_id != current_user.id]
        best_opponent_score = max((player.score for player in others), default=own.score)
        outcome = "win" if own.score > best_opponent_score else "draw" if own.score == best_opponent_score else "loss"
        history.append({
            "room_code": room.code,
            "status": room.status,
            "game_mode": room.board_game_mode or room.game_mode,
            "score": own.score,
            "opponent_score": best_opponent_score,
            "outcome": outcome,
            "opponents": [player.user.username if player.user else f"Player {player.user_id}" for player in others],
            "played_at": room.finished_at or room.created_at,
        })
    return ResponseSchema(data=history, message="Đã tải lịch sử trận đấu")
