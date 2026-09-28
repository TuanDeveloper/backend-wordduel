import json

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.learning import FriendRequest, Notification
from app.models.room import Room, RoomPlayer
from app.models.user import User
from app.schemas.response import ResponseSchema
from app.services import room_service
from app.websockets.connection_manager import manager

router = APIRouter(prefix="/social", tags=["social"])


class FriendRequestCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)


class RoomInviteCreate(BaseModel):
    friend_id: int = Field(gt=0)
    room_code: str = Field(min_length=4, max_length=10)


def _friend_request(db: Session, first_id: int, second_id: int) -> FriendRequest | None:
    return db.query(FriendRequest).filter(
        or_(
            (FriendRequest.requester_id == first_id) & (FriendRequest.recipient_id == second_id),
            (FriendRequest.requester_id == second_id) & (FriendRequest.recipient_id == first_id),
        )
    ).first()


def _friends(db: Session, user_id: int) -> list[int]:
    requests = db.query(FriendRequest).filter(
        FriendRequest.status == "accepted",
        or_(FriendRequest.requester_id == user_id, FriendRequest.recipient_id == user_id),
    ).all()
    return [request.recipient_id if request.requester_id == user_id else request.requester_id for request in requests]


def _friend_data(db: Session, user: User) -> dict:
    playing = db.query(Room.code).join(RoomPlayer, RoomPlayer.room_id == Room.id).filter(
        RoomPlayer.user_id == user.id, Room.status == "playing"
    ).first()
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "avatar_key": user.avatar_key,
        "is_online": manager.user_is_online(user.id),
        "is_playing": playing is not None,
        "room_code": playing[0] if playing else None,
    }


def _notification_payload(notification: Notification) -> dict:
    return {
        "id": notification.id,
        "type": notification.notification_type,
        "title": notification.title,
        "body": notification.body,
        "payload": notification.payload or {},
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
    }


async def _notify(db: Session, recipient_id: int, actor_id: int | None, kind: str, title: str, body: str, payload: dict) -> Notification:
    notification = Notification(
        recipient_id=recipient_id,
        actor_id=actor_id,
        notification_type=kind,
        title=title,
        body=body,
        payload=payload,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    await manager.broadcast_user(recipient_id, {"event": "notification", "notification": _notification_payload(notification)})
    return notification


@router.get("/search", response_model=ResponseSchema[list[dict]])
def search_users(
    q: str = Query(min_length=2, max_length=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[list[dict]]:
    pattern = f"%{q.strip()}%"
    users = db.query(User).filter(
        User.id != current_user.id,
        User.is_active.is_(True),
        or_(User.username.ilike(pattern), User.full_name.ilike(pattern)),
    ).order_by(User.username).limit(20).all()
    accepted = set(_friends(db, current_user.id))
    results = []
    for user in users:
        request = _friend_request(db, current_user.id, user.id)
        results.append({
            **_friend_data(db, user),
            "friend_status": "friend" if user.id in accepted else request.status if request else None,
            "request_direction": "incoming" if request and request.recipient_id == current_user.id and request.status == "pending" else "outgoing" if request and request.status == "pending" else None,
        })
    return ResponseSchema(data=results, message="Đã tìm người chơi")


@router.get("/friends", response_model=ResponseSchema[list[dict]])
def list_friends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[list[dict]]:
    friends = [db.get(User, friend_id) for friend_id in _friends(db, current_user.id)]
    data = [_friend_data(db, friend) for friend in friends if friend and friend.is_active]
    data.sort(key=lambda friend: (not friend["is_online"], friend["username"].casefold()))
    return ResponseSchema(data=data, message="Đã tải danh sách bạn bè")


@router.get("/requests", response_model=ResponseSchema[dict])
def list_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    rows = db.query(FriendRequest).filter(
        FriendRequest.status == "pending",
        or_(FriendRequest.recipient_id == current_user.id, FriendRequest.requester_id == current_user.id),
    ).order_by(FriendRequest.created_at.desc()).all()
    incoming, outgoing = [], []
    for row in rows:
        other_id = row.requester_id if row.recipient_id == current_user.id else row.recipient_id
        other = db.get(User, other_id)
        item = {"id": row.id, "user": _friend_data(db, other)} if other else None
        if item:
            (incoming if row.recipient_id == current_user.id else outgoing).append(item)
    return ResponseSchema(data={"incoming": incoming, "outgoing": outgoing}, message="Đã tải lời mời kết bạn")


@router.post("/requests", response_model=ResponseSchema[dict])
async def send_friend_request(
    request: FriendRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    recipient = db.query(User).filter(User.username.ilike(request.username.strip()), User.is_active.is_(True)).first()
    if not recipient:
        raise NotFoundError("Không tìm thấy người chơi")
    if recipient.id == current_user.id:
        raise BadRequestError("Bạn không thể kết bạn với chính mình")
    existing = _friend_request(db, current_user.id, recipient.id)
    if existing and existing.status == "accepted":
        raise BadRequestError("Hai bạn đã là bạn bè")
    if existing and existing.status == "pending":
        if existing.requester_id == recipient.id:
            existing.status = "accepted"
            db.commit()
            await _notify(db, recipient.id, current_user.id, "friend_accepted", "Lời mời được chấp nhận", f"{current_user.username} đã chấp nhận lời mời kết bạn.", {"friend_id": current_user.id})
            return ResponseSchema(data={"friend_status": "friend"}, message="Đã chấp nhận lời mời kết bạn")
        raise BadRequestError("Lời mời kết bạn đã được gửi")
    row = FriendRequest(requester_id=current_user.id, recipient_id=recipient.id)
    db.add(row)
    db.commit()
    await _notify(db, recipient.id, current_user.id, "friend_request", "Lời mời kết bạn", f"{current_user.username} muốn kết bạn với bạn.", {"request_id": row.id})
    return ResponseSchema(data={"id": row.id, "friend_status": "pending"}, message="Đã gửi lời mời kết bạn")


@router.post("/requests/{request_id}/accept", response_model=ResponseSchema[dict])
async def accept_friend_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    row = db.query(FriendRequest).filter(FriendRequest.id == request_id).first()
    if not row:
        raise NotFoundError("Không tìm thấy lời mời kết bạn")
    if row.recipient_id != current_user.id or row.status != "pending":
        raise ForbiddenError("Bạn không thể chấp nhận lời mời này")
    row.status = "accepted"
    db.commit()
    await _notify(db, row.requester_id, current_user.id, "friend_accepted", "Lời mời được chấp nhận", f"{current_user.username} đã chấp nhận lời mời kết bạn.", {"friend_id": current_user.id})
    return ResponseSchema(data={"friend_id": row.requester_id}, message="Đã kết bạn")


@router.delete("/friends/{friend_id}", response_model=ResponseSchema[dict])
def remove_friend(
    friend_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    row = _friend_request(db, current_user.id, friend_id)
    if not row or row.status != "accepted":
        raise NotFoundError("Không tìm thấy bạn bè")
    db.delete(row)
    db.commit()
    return ResponseSchema(data={"removed": True}, message="Đã xóa khỏi danh sách bạn bè")


@router.post("/invites", response_model=ResponseSchema[dict])
async def invite_friend(
    request: RoomInviteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    if request.friend_id not in _friends(db, current_user.id):
        raise ForbiddenError("Bạn chỉ có thể mời bạn bè trong danh sách")
    room = room_service.get_room_by_code(db, request.room_code.upper())
    if room.host_id != current_user.id or room.status != "waiting":
        raise BadRequestError("Chỉ chủ phòng mới có thể mời bạn vào phòng đang chờ")
    notification = await _notify(db, request.friend_id, current_user.id, "room_invite", "Lời mời vào phòng", f"{current_user.username} mời bạn chơi WordDuel.", {"room_code": room.code})
    return ResponseSchema(data=_notification_payload(notification), message="Đã gửi lời mời vào phòng")


@router.get("/notifications", response_model=ResponseSchema[list[dict]])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[list[dict]]:
    rows = db.query(Notification).filter(Notification.recipient_id == current_user.id).order_by(Notification.created_at.desc()).limit(50).all()
    return ResponseSchema(data=[_notification_payload(row) for row in rows], message="Đã tải thông báo")


@router.post("/notifications/read", response_model=ResponseSchema[dict])
def mark_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    count = db.query(Notification).filter(Notification.recipient_id == current_user.id, Notification.is_read.is_(False)).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return ResponseSchema(data={"updated": count}, message="Đã đọc thông báo")


@router.websocket("/ws/notifications")
async def notification_socket(websocket: WebSocket, db: Session = Depends(get_db)) -> None:
    protocols = websocket.headers.get("sec-websocket-protocol", "")
    token = next((part.strip().removeprefix("bearer.") for part in protocols.split(",") if part.strip().startswith("bearer.")), None)
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        await websocket.close(code=1008, reason="Invalid authentication token")
        return
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        await websocket.close(code=1008, reason="User not found")
        return
    first_connection = await manager.connect_user(websocket, user_id, subprotocol="wordduel")
    friend_ids = _friends(db, user_id)
    if first_connection:
        for friend_id in friend_ids:
            await manager.broadcast_user(friend_id, {"event": "friend_online", "user_id": user_id, "username": user.username})
    try:
        while True:
            message = await websocket.receive_text()
            if len(message) > 1024:
                continue
            if message:
                try:
                    json.loads(message)
                except json.JSONDecodeError:
                    continue
    except WebSocketDisconnect:
        pass
    finally:
        last_connection = manager.disconnect_user(websocket, user_id)
        if last_connection:
            for friend_id in friend_ids:
                await manager.broadcast_user(friend_id, {"event": "friend_offline", "user_id": user_id})
