import json
import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BaseAPIException, BadRequestError, ForbiddenError
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.room import Room, RoomPlayer
from app.models.user import User
from app.schemas.response import ResponseSchema
from app.schemas.room import RoomCreate, RoomResponse, SubmitRequest
from app.services import game_service, room_service
from app.websockets.connection_manager import manager

router = APIRouter()
logger = logging.getLogger(__name__)


def _require_room_member(db: Session, room: Room, user_id: int) -> RoomPlayer:
    player = (
        db.query(RoomPlayer)
        .filter(RoomPlayer.room_id == room.id, RoomPlayer.user_id == user_id)
        .populate_existing()
        .first()
    )
    if not player:
        raise ForbiddenError("Bạn không phải thành viên của phòng")
    return player


def _room_players(room: Room) -> list[dict]:
    return [
        {
            "id": player.id,
            "room_id": room.id,
            "user_id": player.user_id,
            "user": {"username": player.user.username if player.user else f"Player {player.user_id}"},
            "score": player.score,
            "is_ready": player.is_ready,
            "is_host": player.user_id == room.host_id,
            "is_host": player.user_id == room.host_id,
        }
        for player in room.players
    ]


@router.post("", response_model=ResponseSchema[RoomResponse], status_code=status.HTTP_201_CREATED)
def create_room(
    room_in: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[RoomResponse]:
    room = room_service.create_room(db, room_in=room_in, host_id=current_user.id)
    return ResponseSchema(data=room, message="Tạo phòng chơi thành công")


@router.get("/{code}", response_model=ResponseSchema[RoomResponse])
def get_room(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[RoomResponse]:
    room = room_service.get_room_by_code(db, code=code)
    _require_room_member(db, room, current_user.id)
    return ResponseSchema(data=room, message="Lấy thông tin phòng thành công")


@router.get("/{code}/game-state", response_model=ResponseSchema[dict])
def get_game_state(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    state = game_service.get_game_state(db, room_code=code, user_id=current_user.id)
    return ResponseSchema(data=state, message="Lấy trạng thái trận đấu thành công")


@router.post("/{code}/join", response_model=ResponseSchema[RoomResponse])
async def join_room(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[RoomResponse]:
    room = room_service.join_room(db, code=code, user_id=current_user.id)
    await manager.broadcast(code, {"event": "player_joined", "players": _room_players(room), "host_id": room.host_id})
    return ResponseSchema(data=room, message="Tham gia phòng chơi thành công")


@router.post("/{code}/leave", response_model=ResponseSchema[dict])
async def leave_room(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    room = db.query(Room).filter(Room.code == code).with_for_update().populate_existing().first()
    if not room:
        raise BadRequestError("Phòng chơi không còn tồn tại")
    player = _require_room_member(db, room, current_user.id)
    was_host = room.host_id == current_user.id
    db.delete(player)
    db.flush()
    remaining = (
        db.query(RoomPlayer)
        .filter(RoomPlayer.room_id == room.id)
        .order_by(RoomPlayer.joined_at.asc(), RoomPlayer.id.asc())
        .all()
    )
    if not remaining:
        db.delete(room)
        db.commit()
        await manager.broadcast(code, {"event": "room_closed", "reason": "empty", "players": []})
        return ResponseSchema(data={"left": True, "closed": True}, message="Đã đóng phòng trống")

    if was_host:
        room.host_id = remaining[0].user_id
    db.commit()
    room = room_service.get_room_by_code(db, code)
    await manager.broadcast(code, {
        "event": "player_left",
        "user_id": current_user.id,
        "username": current_user.username,
        "host_id": room.host_id,
        "players": _room_players(room),
    })
    return ResponseSchema(data={"left": True, "closed": False, "host_id": room.host_id}, message="Đã rời phòng")


@router.post("/{code}/ready", response_model=ResponseSchema[dict])
async def toggle_ready(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    room = room_service.get_room_by_code(db, code=code)
    player = _require_room_member(db, room, current_user.id)
    if room.status != "waiting":
        raise BadRequestError("Chỉ có thể đổi trạng thái sẵn sàng khi phòng đang chờ")
    player.is_ready = not player.is_ready
    db.commit()
    await manager.broadcast(code, {
        "event": "player_ready",
        "user_id": current_user.id,
        "is_ready": player.is_ready,
        "players": _room_players(room),
    })
    return ResponseSchema(data={"is_ready": player.is_ready}, message="Cập nhật trạng thái sẵn sàng")


@router.post("/{code}/start", response_model=ResponseSchema[dict])
async def start_room_game(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    game_data = game_service.start_game(db, room_code=code, user_id=current_user.id)
    await manager.broadcast(code, game_data)
    return ResponseSchema(data=game_data, message="Bắt đầu trận đấu thành công")


@router.post("/{code}/submit", response_model=ResponseSchema[dict])
async def submit_room_answer(
    code: str,
    submit_in: SubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    feedback = game_service.submit_answer(
        db,
        room_code=code,
        user_id=current_user.id,
        word_id=submit_in.word_id,
        submitted_answer=submit_in.submitted_answer,
        question_index=submit_in.question_index,
    )
    await manager.broadcast(code, game_service.public_progress_update(feedback, current_user.id))
    return ResponseSchema(data=feedback, message="Nộp câu trả lời thành công")


@router.post("/{code}/finish", response_model=ResponseSchema[dict])
async def finish_room_game(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    finish_data = game_service.finish_game(db, room_code=code, user_id=current_user.id)
    await manager.broadcast(code, finish_data)
    return ResponseSchema(data=finish_data, message="Kết thúc ván đấu")


def _websocket_token(websocket: WebSocket) -> str | None:
    offered_protocols = websocket.headers.get("sec-websocket-protocol", "")
    for protocol in (part.strip() for part in offered_protocols.split(",")):
        if protocol.startswith("bearer."):
            return protocol.removeprefix("bearer.")
    return None


async def handle_websocket_connection(websocket: WebSocket, code: str, db: Session) -> None:
    token = _websocket_token(websocket)
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        await websocket.close(code=1008, reason="Invalid authentication token")
        return

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        await websocket.close(code=1008, reason="User not found")
        return

    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        await websocket.close(code=1008, reason="Room not found")
        return
    try:
        player = _require_room_member(db, room, user_id)
    except BaseAPIException:
        await websocket.close(code=1008, reason="Room membership required")
        return
    username = player.user.username if player.user else user.username

    await manager.connect(websocket, code, user_id, subprotocol="wordduel")
    try:
        await manager.broadcast(code, {
            "event": "player_joined",
            "user_id": user_id,
            "username": username,
            "players": _room_players(room),
        })

        while True:
            raw_message = await websocket.receive_text()
            db.refresh(user)
            if not user.is_active:
                await websocket.close(code=1008, reason="Account is disabled")
                break
            if len(raw_message) > 8192:
                await manager.send_personal(websocket, {"event": "error", "message": "Tin nhắn quá dài"})
                continue
            try:
                message = json.loads(raw_message)
                if not isinstance(message, dict):
                    raise ValueError("Expected a JSON object")
                event = message.get("event") or message.get("type")

                if event == "chat":
                    chat_text = message.get("message", "")
                    if isinstance(chat_text, str) and len(chat_text) <= 1000:
                        await manager.broadcast(code, {
                            "event": "chat",
                            "user_id": user_id,
                            "username": username,
                            "message": chat_text,
                        })
                elif event == "ready":
                    db.refresh(room)
                    room_player = _require_room_member(db, room, user_id)
                    if room.status != "waiting":
                        raise BadRequestError("Chỉ có thể đổi trạng thái sẵn sàng khi phòng đang chờ")
                    ready_value = message.get("is_ready", True)
                    if not isinstance(ready_value, bool):
                        raise BadRequestError("Trạng thái sẵn sàng không hợp lệ")
                    room_player.is_ready = ready_value
                    db.commit()
                    await manager.broadcast(code, {
                        "event": "player_ready",
                        "user_id": user_id,
                        "is_ready": room_player.is_ready,
                        "players": _room_players(room),
                    })
                elif event == "start":
                    game_data = game_service.start_game(db, room_code=code, user_id=user_id)
                    await manager.broadcast(code, game_data)
                elif event == "submit":
                    word_id = message.get("word_id")
                    answer = message.get("answer", "")
                    if (
                        not isinstance(word_id, int)
                        or isinstance(word_id, bool)
                        or not isinstance(answer, str)
                        or len(answer) > 255
                    ):
                        raise ValueError("Invalid answer payload")
                    question_index = message.get("question_index", 0)
                    if not isinstance(question_index, int) or isinstance(question_index, bool):
                        raise ValueError("Invalid question index")
                    feedback = game_service.submit_answer(
                        db, room_code=code, user_id=user_id, word_id=word_id,
                        submitted_answer=answer, question_index=question_index,
                    )
                    await manager.broadcast(code, game_service.public_progress_update(feedback, user_id))
                    await manager.send_personal(websocket, feedback)
                elif event == "finish":
                    finish_data = game_service.finish_game(db, room_code=code, user_id=user_id)
                    await manager.broadcast(code, finish_data)
            except BaseAPIException as exc:
                await manager.send_personal(websocket, {"event": "error", "message": exc.message})
            except (ValueError, TypeError, json.JSONDecodeError):
                await manager.send_personal(websocket, {"event": "error", "message": "Dữ liệu gửi lên không hợp lệ"})
            except Exception:
                logger.exception("Failed to process WebSocket event in room %s", code)
                await manager.send_personal(websocket, {"event": "error", "message": "Không thể xử lý yêu cầu"})
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, code)
        try:
            db.expire_all()
            fresh_room = db.query(Room).filter(Room.code == code).first()
            if fresh_room:
                await manager.broadcast(code, {
                    "event": "player_left",
                    "user_id": user_id,
                    "username": username,
                    "players": _room_players(fresh_room),
                })
        except Exception:
            logger.exception("Failed to notify room %s about WebSocket disconnect", code)


@router.websocket("/ws/{code}")
async def websocket_endpoint(
    websocket: WebSocket,
    code: str,
    db: Session = Depends(get_db),
) -> None:
    await handle_websocket_connection(websocket, code, db)
