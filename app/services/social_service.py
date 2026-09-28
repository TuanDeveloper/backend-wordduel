from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.learning import FriendRequest
from app.websockets.connection_manager import manager


async def notify_friends_activity(db: Session, user_ids: list[int], activity: str) -> None:
    for user_id in set(user_ids):
        requests = db.query(FriendRequest).filter(
            FriendRequest.status == "accepted",
            or_(FriendRequest.requester_id == user_id, FriendRequest.recipient_id == user_id),
        ).all()
        friend_ids = [row.recipient_id if row.requester_id == user_id else row.requester_id for row in requests]
        for friend_id in friend_ids:
            await manager.broadcast_user(friend_id, {"event": "friend_activity", "user_id": user_id, "activity": activity})
