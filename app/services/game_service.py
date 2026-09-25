"""
GameService — xử lý logic game:
  - Lưu tiến độ tạm thời vào Redis (correct_count, total_count) với fallback in-memory
  - So sánh đáp án
  - Lưu Submission vào PostgreSQL
  - Broadcast progress_update
  - Xác định người thắng và lưu kết quả cuối
"""
import json
from datetime import datetime
from typing import Any
from sqlalchemy.orm import Session

from app.core.redis import get_redis
from app.models.room import Room, RoomPlayer, Submission
from app.models.word import Word
from app.core.exceptions import NotFoundError, BadRequestError

# Fallback in-memory storage if Redis is unavailable
_memory_progress: dict[str, dict[str, Any]] = {}
_memory_words: dict[str, list[int]] = {}


def _progress_key(room_code: str, user_id: int) -> str:
    return f"wordduel:room:{room_code}:player:{user_id}:progress"


def _room_words_key(room_code: str) -> str:
    return f"wordduel:room:{room_code}:words"


def start_game(db: Session, room_code: str) -> dict:
    room = db.query(Room).filter(Room.code == room_code).first()
    if not room:
        raise NotFoundError("Không tìm thấy phòng")
    if room.status != "waiting":
        raise BadRequestError("Phòng không ở trạng thái chờ")

    room.status = "playing"
    db.commit()
    db.refresh(room)

    words = db.query(Word).filter(Word.word_set_id == room.word_set_id).all()
    word_ids = [w.id for w in words]
    words_data = [
        {"id": w.id, "term": w.term, "definition": w.definition, "example": w.example}
        for w in words
    ]

    try:
        r = get_redis()
        r.set(_room_words_key(room_code), json.dumps(word_ids), ex=3600)
        for player in room.players:
            key = _progress_key(room_code, player.user_id)
            r.hset(key, mapping={"correct": 0, "total": 0})
            r.expire(key, 3600)
    except Exception:
        _memory_words[room_code] = word_ids
        for player in room.players:
            _memory_progress[f"{room_code}_{player.user_id}"] = {"correct": 0, "total": 0}

    return {
        "event": "game_started",
        "room_code": room_code,
        "word_set_id": room.word_set_id,
        "total_words": len(word_ids),
        "words": words_data,
        "players": [p.user_id for p in room.players],
    }


def submit_answer(
    db: Session,
    room_code: str,
    user_id: int,
    word_id: int,
    submitted_answer: str,
) -> dict:
    room = db.query(Room).filter(Room.code == room_code).first()
    if not room:
        raise NotFoundError("Không tìm thấy phòng")
    if room.status != "playing":
        raise BadRequestError("Phòng chưa bắt đầu hoặc đã kết thúc")

    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise NotFoundError("Không tìm thấy từ")

    clean_sub = submitted_answer.strip().lower()
    # Đáp án đúng nếu khớp term hoặc definition
    is_correct = clean_sub in [word.term.strip().lower(), word.definition.strip().lower()]

    submission = Submission(
        room_id=room.id,
        user_id=user_id,
        word_id=word_id,
        submitted_answer=submitted_answer,
        is_correct=is_correct,
    )
    db.add(submission)
    db.commit()

    # Cập nhật tiến độ
    try:
        r = get_redis()
        key = _progress_key(room_code, user_id)
        r.hincrby(key, "total", 1)
        if is_correct:
            r.hincrby(key, "correct", 1)
    except Exception:
        mem_key = f"{room_code}_{user_id}"
        cur = _memory_progress.get(mem_key, {"correct": 0, "total": 0})
        cur["total"] = cur.get("total", 0) + 1
        if is_correct:
            cur["correct"] = cur.get("correct", 0) + 1
        _memory_progress[mem_key] = cur

    if is_correct:
        player = (
            db.query(RoomPlayer)
            .filter(RoomPlayer.room_id == room.id, RoomPlayer.user_id == user_id)
            .first()
        )
        if player:
            player.score += 1
            db.commit()

    players_progress = _get_all_progress(room_code, room)

    return {
        "event": "progress_update",
        "room_code": room_code,
        "submitter": user_id,
        "is_correct": is_correct,
        "correct_answer": word.term,
        "definition": word.definition,
        "players": players_progress,
    }


def _get_all_progress(room_code: str, room: Room) -> list[dict]:
    result = []
    try:
        r = get_redis()
        for player in room.players:
            key = _progress_key(room_code, player.user_id)
            data = r.hgetall(key)
            result.append(
                {
                    "user_id": player.user_id,
                    "username": player.user.username if player.user else f"Player {player.user_id}",
                    "correct": int(data.get("correct", 0)),
                    "total": int(data.get("total", 0)),
                    "score": player.score,
                }
            )
    except Exception:
        for player in room.players:
            cur = _memory_progress.get(f"{room_code}_{player.user_id}", {"correct": 0, "total": 0})
            result.append(
                {
                    "user_id": player.user_id,
                    "username": player.user.username if player.user else f"Player {player.user_id}",
                    "correct": cur.get("correct", 0),
                    "total": cur.get("total", 0),
                    "score": player.score,
                }
            )
    return result


def finish_game(db: Session, room_code: str) -> dict:
    room = db.query(Room).filter(Room.code == room_code).first()
    if not room:
        raise NotFoundError("Không tìm thấy phòng")

    room.status = "finished"
    room.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(room)

    players_sorted = sorted(room.players, key=lambda p: p.score, reverse=True)
    leaderboard = [
        {
            "rank": idx + 1,
            "user_id": p.user_id,
            "username": p.user.username if p.user else f"Player {p.user_id}",
            "score": p.score,
        }
        for idx, p in enumerate(players_sorted)
    ]

    winner = players_sorted[0] if players_sorted else None

    return {
        "event": "game_finished",
        "room_code": room_code,
        "winner_user_id": winner.user_id if winner else None,
        "winner_username": winner.user.username if winner and winner.user else None,
        "leaderboard": leaderboard,
    }
