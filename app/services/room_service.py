import random
import string
from typing import Optional
from sqlalchemy.orm import Session

from app.models.room import Room, RoomPlayer
from app.models.word import WordSet
from app.schemas.room import RoomCreate
from app.core.exceptions import NotFoundError, BadRequestError


def generate_room_code(db: Session, length: int = 6) -> str:
    """Sinh mã phòng ngẫu nhiên và đảm bảo duy nhất trong các phòng chưa kết thúc"""
    characters = string.ascii_uppercase + string.digits
    for _ in range(10):  # Thử tối đa 10 lần tránh vòng lặp vô tận
        code = "".join(random.choices(characters, k=length))
        existing_room = (
            db.query(Room)
            .filter(Room.code == code, Room.status.in_(["waiting", "playing"]))
            .first()
        )
        if not existing_room:
            return code
    # Nếu bị trùng nhiều lần, tăng độ dài code
    return "".join(random.choices(characters, k=length + 2))


def get_room_by_code(db: Session, code: str) -> Room:
    """Lấy thông tin chi tiết phòng theo mã phòng"""
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise NotFoundError("Không tìm thấy phòng chơi với mã này")
    return room


def create_room(db: Session, room_in: RoomCreate, host_id: int) -> Room:
    """Tạo phòng chơi mới và tự động thêm host vào phòng"""
    # 1. Kiểm tra bộ từ vựng có tồn tại không
    word_set = db.query(WordSet).filter(WordSet.id == room_in.word_set_id).first()
    if not word_set:
        raise NotFoundError("Bộ từ vựng không tồn tại")

    # 2. Sinh mã phòng
    code = generate_room_code(db)

    # 3. Tạo phòng
    room = Room(
        code=code,
        host_id=host_id,
        word_set_id=room_in.word_set_id,
        status="waiting",
    )
    db.add(room)
    db.flush()  # Để lấy room.id

    # 4. Thêm host vào danh sách người chơi
    host_player = RoomPlayer(
        room_id=room.id,
        user_id=host_id,
        is_ready=True,
    )
    db.add(host_player)
    db.commit()
    db.refresh(room)
    return room


def join_room(db: Session, code: str, user_id: int) -> Room:
    """Người chơi tham gia vào phòng chờ"""
    room = get_room_by_code(db, code)

    if room.status != "waiting":
        raise BadRequestError("Phòng đang trong trận đấu hoặc đã kết thúc")

    # Kiểm tra xem người dùng đã tham gia phòng chưa
    existing_player = (
        db.query(RoomPlayer)
        .filter(RoomPlayer.room_id == room.id, RoomPlayer.user_id == user_id)
        .first()
    )

    if not existing_player:
        player = RoomPlayer(
            room_id=room.id,
            user_id=user_id,
            is_ready=False,
        )
        db.add(player)
        db.commit()
        db.refresh(room)

    return room
