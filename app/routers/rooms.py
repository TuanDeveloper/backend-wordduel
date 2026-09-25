import json
from typing import Any
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.room import Room, RoomPlayer
from app.services import room_service, game_service
from app.schemas.room import RoomCreate, RoomResponse, SubmitRequest
from app.schemas.response import ResponseSchema
from app.websockets.connection_manager import manager
from app.core.config import settings

router = APIRouter()


@router.post("", response_model=ResponseSchema[RoomResponse], status_code=status.HTTP_201_CREATED)
def create_room(
    room_in: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[RoomResponse]:
    """Tạo phòng chơi mới và sinh mã phòng ngẫu nhiên."""
    room = room_service.create_room(db, room_in=room_in, host_id=current_user.id)
    return ResponseSchema(data=room, message="Tạo phòng chơi thành công")


@router.get("/{code}", response_model=ResponseSchema[RoomResponse])
def get_room(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[RoomResponse]:
    """Lấy thông tin chi tiết phòng chơi theo mã code."""
    room = room_service.get_room_by_code(db, code=code)
    return ResponseSchema(data=room, message="Lấy thông tin phòng thành công")


@router.post("/{code}/join", response_model=ResponseSchema[RoomResponse])
def join_room(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[RoomResponse]:
    """Tham gia vào phòng chơi theo mã code."""
    room = room_service.join_room(db, code=code, user_id=current_user.id)
    return ResponseSchema(data=room, message="Tham gia phòng chơi thành công")


@router.post("/{code}/ready", response_model=ResponseSchema[dict])
async def toggle_ready(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    """Toggle trạng thái ready của người chơi trong phòng."""
    room = room_service.get_room_by_code(db, code=code)
    player = db.query(RoomPlayer).filter(RoomPlayer.room_id == room.id, RoomPlayer.user_id == current_user.id).first()
    if player:
        player.is_ready = not player.is_ready
        db.commit()
    
    # Broadcast cập nhật
    await manager.broadcast(code, {
        "event": "player_ready",
        "user_id": current_user.id,
        "is_ready": player.is_ready if player else False,
    })
    return ResponseSchema(data={"is_ready": player.is_ready if player else False}, message="Cập nhật trạng thái sẵn sàng")


@router.post("/{code}/start", response_model=ResponseSchema[dict])
async def start_room_game(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    """Host bắt đầu trận đấu."""
    game_data = game_service.start_game(db, room_code=code)
    # Broadcast qua WebSocket
    await manager.broadcast(code, game_data)
    return ResponseSchema(data=game_data, message="Bắt đầu trận đấu thành công")


@router.post("/{code}/submit", response_model=ResponseSchema[dict])
async def submit_room_answer(
    code: str,
    submit_in: SubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    """Nộp câu trả lời cho một câu hỏi."""
    progress_data = game_service.submit_answer(
        db,
        room_code=code,
        user_id=current_user.id,
        word_id=submit_in.word_id,
        submitted_answer=submit_in.submitted_answer,
    )
    # Broadcast cập nhật điểm / tiến độ
    await manager.broadcast(code, progress_data)
    return ResponseSchema(data=progress_data, message="Nộp câu trả lời thành công")


@router.post("/{code}/finish", response_model=ResponseSchema[dict])
async def finish_room_game(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    """Kết thúc ván đấu và tính kết quả."""
    finish_data = game_service.finish_game(db, room_code=code)
    await manager.broadcast(code, finish_data)
    return ResponseSchema(data=finish_data, message="Kết thúc ván đấu")


async def handle_websocket_connection(websocket: WebSocket, code: str, db: Session):
    token = websocket.query_params.get("token")
    user_id = None
    username = "Anonymous"

    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = int(payload.get("sub"))
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                username = user.username
        except (JWTError, ValueError, Exception):
            pass

    if not user_id:
        # Nếu không có token hợp lệ, tạm gán user_id từ timestamp
        user_id = int(websocket.headers.get("sec-websocket-key", "0")[:5], 16) % 100000

    await manager.connect(websocket, code, user_id)

    # Lấy thông tin phòng và người chơi
    room = db.query(Room).filter(Room.code == code).first()
    players_info = []
    if room:
        for p in room.players:
            players_info.append({
                "user_id": p.user_id,
                "username": p.user.username if p.user else f"Player {p.user_id}",
                "score": p.score,
                "is_ready": p.is_ready,
                "is_host": p.user_id == room.host_id,
            })

    # Broadcast người chơi mới tham gia
    await manager.broadcast(code, {
        "event": "player_joined",
        "user_id": user_id,
        "username": username,
        "players": players_info,
    })

    try:
        while True:
            text = await websocket.receive_text()
            try:
                msg = json.loads(text)
                event = msg.get("event") or msg.get("type")

                if event == "chat":
                    await manager.broadcast(code, {
                        "event": "chat",
                        "user_id": user_id,
                        "username": username,
                        "message": msg.get("message", ""),
                    })
                elif event == "ready":
                    is_ready = bool(msg.get("is_ready", True))
                    if room:
                        rp = db.query(RoomPlayer).filter(RoomPlayer.room_id == room.id, RoomPlayer.user_id == user_id).first()
                        if rp:
                            rp.is_ready = is_ready
                            db.commit()
                    await manager.broadcast(code, {
                        "event": "player_ready",
                        "user_id": user_id,
                        "is_ready": is_ready,
                    })
                elif event == "start":
                    game_data = game_service.start_game(db, room_code=code)
                    await manager.broadcast(code, game_data)
                elif event == "submit":
                    word_id = msg.get("word_id")
                    answer = msg.get("answer", "")
                    progress_data = game_service.submit_answer(
                        db, room_code=code, user_id=user_id, word_id=word_id, submitted_answer=answer
                    )
                    await manager.broadcast(code, progress_data)
                elif event == "finish":
                    finish_data = game_service.finish_game(db, room_code=code)
                    await manager.broadcast(code, finish_data)
            except Exception as e:
                await manager.send_personal(websocket, {"event": "error", "message": str(e)})
    except WebSocketDisconnect:
        manager.disconnect(websocket, code)
        await manager.broadcast(code, {
            "event": "player_left",
            "user_id": user_id,
            "username": username,
        })


@router.websocket("/ws/{code}")
async def websocket_endpoint(
    websocket: WebSocket,
    code: str,
    db: Session = Depends(get_db),
):
    await handle_websocket_connection(websocket, code, db)
