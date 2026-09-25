import secrets
import string

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models.room import Room, RoomPlayer
from app.models.word import Word, WordSet
from app.schemas.room import RoomCreate


def generate_room_code(db: Session, length: int = 6) -> str:
    """Generate a cryptographically random code unused by any existing room."""
    characters = string.ascii_uppercase + string.digits
    for _ in range(20):
        code = "".join(secrets.choice(characters) for _ in range(length))
        if not db.query(Room.id).filter(Room.code == code).first():
            return code
    raise ConflictError("Không thể tạo mã phòng duy nhất, vui lòng thử lại")


def get_room_by_code(db: Session, code: str) -> Room:
    room = (
        db.query(Room)
        .options(joinedload(Room.players).joinedload(RoomPlayer.user))
        .filter(Room.code == code)
        .first()
    )
    if not room:
        raise NotFoundError("Không tìm thấy phòng chơi với mã này")
    return room


def create_room(db: Session, room_in: RoomCreate, host_id: int) -> Room:
    word_set = db.query(WordSet).filter(WordSet.id == room_in.word_set_id, WordSet.is_hidden.is_(False)).first()
    if not word_set:
        raise NotFoundError("Bộ từ vựng không tồn tại")
    available_words = db.query(func.count(Word.id)).filter(Word.word_set_id == word_set.id).scalar() or 0
    if not available_words:
        raise BadRequestError("Bộ từ vựng chưa có từ nào")
    word_count = min(room_in.word_count or available_words, available_words, 500)
    question_count = room_in.question_count or word_count

    # The unique index remains authoritative if another process picks the same code.
    for _ in range(5):
        code = generate_room_code(db)
        room = Room(
            code=code,
            host_id=host_id,
            word_set_id=room_in.word_set_id,
            word_count=word_count,
            time_per_question=room_in.time_per_question,
            question_count=question_count,
            status="waiting",
        )
        db.add(room)
        try:
            db.flush()
            db.add(RoomPlayer(room_id=room.id, user_id=host_id, is_ready=True))
            db.commit()
            db.refresh(room)
            return room
        except IntegrityError:
            db.rollback()
            if db.query(Room.id).filter(Room.code == code).first():
                continue
            raise
    raise ConflictError("Không thể tạo mã phòng duy nhất, vui lòng thử lại")


def join_room(db: Session, code: str, user_id: int) -> Room:
    room = db.query(Room).filter(Room.code == code).with_for_update().populate_existing().first()
    if not room:
        raise NotFoundError("Không tìm thấy phòng chơi với mã này")
    if room.status != "waiting":
        raise BadRequestError("Phòng đang trong trận đấu hoặc đã kết thúc")

    existing_player = (
        db.query(RoomPlayer)
        .filter(RoomPlayer.room_id == room.id, RoomPlayer.user_id == user_id)
        .first()
    )
    if not existing_player:
        db.add(RoomPlayer(room_id=room.id, user_id=user_id, is_ready=False))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            # A concurrent join by this same user is an idempotent success.
            existing_player = (
                db.query(RoomPlayer)
                .filter(RoomPlayer.room_id == room.id, RoomPlayer.user_id == user_id)
                .first()
            )
            if not existing_player:
                raise
    db.refresh(room)
    return get_room_by_code(db, code)
