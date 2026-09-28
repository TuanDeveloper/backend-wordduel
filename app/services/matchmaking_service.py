from datetime import datetime, timedelta
import random

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.matchmaking import MatchmakingEntry
from app.models.room import Room, RoomPlayer
from app.models.word import Word, WordSet
from app.services.room_service import generate_room_code


QUEUE_TTL = timedelta(minutes=10)


def _room_details(db: Session, entry: MatchmakingEntry) -> dict:
    room = db.query(Room).filter(Room.id == entry.room_id).first() if entry.room_id else None
    return {"status": entry.status, "room_code": room.code if room else None, "game_mode": entry.game_mode, "board_game_mode": entry.board_game_mode}


def search(db: Session, user_id: int, game_mode: str, board_game_mode: str | None) -> dict:
    # Serialize a user's concurrent clicks/polls; the partial unique index remains
    # the cross-process integrity backstop.
    db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": user_id})
    now = datetime.utcnow()
    # Expire abandoned browsers so stale entries never block or attract players.
    db.query(MatchmakingEntry).filter(
        MatchmakingEntry.status == "searching", MatchmakingEntry.created_at < now - QUEUE_TTL
    ).update({"status": "expired"}, synchronize_session=False)

    entry = (db.query(MatchmakingEntry).filter(
        MatchmakingEntry.user_id == user_id, MatchmakingEntry.status == "searching"
    ).with_for_update().first())
    if entry:
        if entry.game_mode != game_mode or entry.board_game_mode != board_game_mode:
            entry.status = "cancelled"
            db.flush()
        # Repeated search/status checks also attempt a match. This handles the
        # case where two users entered the queue at almost exactly the same time.
        else:
            pass

    if not entry or entry.status != "searching":
        entry = MatchmakingEntry(user_id=user_id, game_mode=game_mode, board_game_mode=board_game_mode, status="searching")
        db.add(entry)
        db.flush()

    # Lock one compatible entry; SKIP LOCKED prevents concurrent requests matching
    # the same player. Selection is randomized among currently available candidates.
    candidates = (db.query(MatchmakingEntry)
        .filter(
            MatchmakingEntry.status == "searching",
            MatchmakingEntry.user_id != user_id,
            MatchmakingEntry.game_mode == game_mode,
            MatchmakingEntry.board_game_mode == board_game_mode,
            MatchmakingEntry.created_at >= now - QUEUE_TTL,
        )
        .with_for_update(skip_locked=True)
        .all())
    if not candidates:
        db.commit()
        return _room_details(db, entry)

    opponent = random.choice(candidates)
    available_set = (db.query(WordSet.id, func.count(Word.id).label("word_count"))
        .join(Word, Word.word_set_id == WordSet.id)
        .filter(WordSet.is_hidden.is_(False))
        .group_by(WordSet.id)
        .having(func.count(Word.id) > 0)
        .all())
    if not available_set:
        raise BadRequestError("Chưa có bộ từ vựng công khai nào có từ để bắt đầu trận")
    set_id, total_words = random.choice(available_set)
    code = generate_room_code(db)
    room = Room(
        code=code, host_id=opponent.user_id, word_set_id=set_id, word_set_ids=[set_id],
        points_per_correct=1, word_count=min(total_words, 20), time_per_question=20,
        question_count=min(total_words, 10), game_mode=game_mode,
        board_game_mode=board_game_mode, status="waiting",
    )
    db.add(room)
    db.flush()
    db.add_all([
        RoomPlayer(room_id=room.id, user_id=opponent.user_id, is_ready=True),
        RoomPlayer(room_id=room.id, user_id=user_id, is_ready=True),
    ])
    opponent.status = "matched"
    opponent.room_id = room.id
    opponent.matched_at = now
    entry.status = "matched"
    entry.room_id = room.id
    entry.matched_at = now
    db.commit()
    return _room_details(db, entry)


def status(db: Session, user_id: int) -> dict:
    entry = (db.query(MatchmakingEntry)
        .filter(MatchmakingEntry.user_id == user_id)
        .order_by(MatchmakingEntry.created_at.desc())
        .first())
    if not entry:
        raise NotFoundError("Bạn hiện không ở trong hàng chờ tìm trận")
    if entry.status == "searching":
        return search(db, user_id, entry.game_mode, entry.board_game_mode)
    return _room_details(db, entry)


def cancel(db: Session, user_id: int) -> dict:
    entry = (db.query(MatchmakingEntry)
        .filter(MatchmakingEntry.user_id == user_id, MatchmakingEntry.status == "searching")
        .with_for_update().first())
    if entry:
        entry.status = "cancelled"
        db.commit()
    else:
        db.rollback()
    return {"status": "cancelled"}
