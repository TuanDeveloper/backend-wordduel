from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.response import ResponseSchema

router = APIRouter(prefix="/rankings", tags=["rankings"])


def _tier(rating: int) -> str:
    if rating >= 1800:
        return "Huyền thoại"
    if rating >= 1600:
        return "Cao thủ"
    if rating >= 1400:
        return "Kim cương"
    if rating >= 1200:
        return "Bạch kim"
    if rating >= 1000:
        return "Vàng"
    return "Tân thủ"


@router.get("", response_model=ResponseSchema[dict])
def get_rankings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ranked_users = (db.query(User)
        .filter(User.is_active.is_(True), User.rated_games > 0)
        .order_by(User.rating.desc(), User.wins.desc(), User.rated_games.desc(), User.username.asc())
        .all())
    entries = [
        {"rank": index + 1, "user_id": user.id, "username": user.username,
         "avatar_key": user.avatar_key, "rating": user.rating, "rated_games": user.rated_games,
         "wins": user.wins, "tier": _tier(user.rating)}
        for index, user in enumerate(ranked_users)
    ]
    mine = next((entry for entry in entries if entry["user_id"] == current_user.id), None)
    if mine is None:
        mine = {"rank": None, "user_id": current_user.id, "username": current_user.username,
                "avatar_key": current_user.avatar_key, "rating": current_user.rating,
                "rated_games": current_user.rated_games, "wins": current_user.wins,
                "tier": _tier(current_user.rating) if current_user.rated_games > 0 else "Chưa xếp hạng"}
    return ResponseSchema(data={"entries": entries[:100], "current_user": mine, "total_players": len(entries)}, message="Bảng xếp hạng ELO")
