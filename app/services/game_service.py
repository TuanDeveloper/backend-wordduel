"""Game rules and persistence for WordDuel rooms."""

from datetime import datetime
from typing import Any

from sqlalchemy import case, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.room import Room, RoomPlayer, Submission
from app.models.word import Word


def _require_member(db: Session, room: Room, user_id: int) -> RoomPlayer:
    player = (
        db.query(RoomPlayer)
        .filter(RoomPlayer.room_id == room.id, RoomPlayer.user_id == user_id)
        .first()
    )
    if not player:
        raise ForbiddenError("Bạn không phải thành viên của phòng")
    return player


def _public_words(db: Session, word_set_id: int) -> list[dict[str, Any]]:
    return [
        {"id": word.id, "definition": word.definition}
        for word in db.query(Word).filter(Word.word_set_id == word_set_id).order_by(Word.id).all()
    ]


def _leaderboard(room: Room) -> tuple[list[dict[str, Any]], RoomPlayer | None]:
    players_sorted = sorted(
        room.players,
        key=lambda player: (-player.score, player.joined_at or datetime.min),
    )
    leaderboard = [
        {
            "rank": index + 1,
            "user_id": player.user_id,
            "username": player.user.username if player.user else f"Player {player.user_id}",
            "score": player.score,
        }
        for index, player in enumerate(players_sorted)
    ]
    return leaderboard, players_sorted[0] if players_sorted else None


def _finish_payload(room: Room) -> dict[str, Any]:
    leaderboard, winner = _leaderboard(room)
    return {
        "event": "game_finished",
        "room_code": room.code,
        "winner_user_id": winner.user_id if winner else None,
        "winner_username": winner.user.username if winner and winner.user else None,
        "leaderboard": leaderboard,
    }


def start_game(db: Session, room_code: str, user_id: int) -> dict[str, Any]:
    room = db.query(Room).filter(Room.code == room_code).with_for_update().populate_existing().first()
    if not room:
        raise NotFoundError("Không tìm thấy phòng")
    if room.host_id != user_id:
        raise ForbiddenError("Chỉ chủ phòng mới có thể bắt đầu trận đấu")
    if room.status != "waiting":
        raise BadRequestError("Phòng không ở trạng thái chờ")

    players = db.query(RoomPlayer).filter(RoomPlayer.room_id == room.id).populate_existing().all()
    if len(players) < 2 or any(not player.is_ready for player in players):
        raise BadRequestError("Cần ít nhất hai người chơi và tất cả phải sẵn sàng")

    words = db.query(Word).filter(Word.word_set_id == room.word_set_id).order_by(Word.id).all()
    if not words:
        raise BadRequestError("Bộ từ vựng này chưa có từ nào")

    word_ids = [word.id for word in words]
    public_word_data = [{"id": word.id, "definition": word.definition} for word in words]
    player_ids = [player.user_id for player in players]

    room.status = "playing"
    db.commit()

    # Deliberately omit terms and examples; this event goes to every room member.
    return {
        "event": "game_started",
        "room_code": room_code,
        "word_set_id": room.word_set_id,
        "total_words": len(word_ids),
        "words": public_word_data,
        "players": player_ids,
    }


def get_game_state(db: Session, room_code: str, user_id: int) -> dict[str, Any]:
    room = (
        db.query(Room)
        .options(joinedload(Room.players).joinedload(RoomPlayer.user))
        .filter(Room.code == room_code)
        .first()
    )
    if not room:
        raise NotFoundError("Không tìm thấy phòng")
    player = _require_member(db, room, user_id)

    if room.status == "waiting":
        return {"event": "game_waiting", "room_code": room_code, "status": room.status, "host_id": room.host_id}
    if room.status == "finished":
        return _finish_payload(room)

    words = _public_words(db, room.word_set_id)
    answered_word_ids = [
        row[0]
        for row in db.query(Submission.word_id)
        .filter(Submission.room_id == room.id, Submission.user_id == user_id)
        .all()
    ]
    progress = _get_all_progress(db, room)
    return {
        "event": "game_started",
        "room_code": room_code,
        "word_set_id": room.word_set_id,
        "total_words": len(words),
        "words": words,
        "answered_word_ids": answered_word_ids,
        "players": progress,
        "current_user_id": player.user_id,
        "host_id": room.host_id,
    }


def submit_answer(
    db: Session,
    room_code: str,
    user_id: int,
    word_id: int,
    submitted_answer: str,
) -> dict[str, Any]:
    room = db.query(Room).filter(Room.code == room_code).with_for_update().populate_existing().first()
    if not room:
        raise NotFoundError("Không tìm thấy phòng")
    if room.status != "playing":
        raise BadRequestError("Phòng chưa bắt đầu hoặc đã kết thúc")

    player = _require_member(db, room, user_id)
    word = (
        db.query(Word)
        .filter(Word.id == word_id, Word.word_set_id == room.word_set_id)
        .first()
    )
    if not word:
        raise NotFoundError("Từ này không thuộc bộ từ của phòng")

    clean_submitted = submitted_answer.strip().casefold()
    is_correct = clean_submitted == word.term.strip().casefold()
    correct_answer = word.term
    submission = Submission(
        room_id=room.id,
        user_id=user_id,
        word_id=word_id,
        submitted_answer=submitted_answer.strip(),
        is_correct=is_correct,
    )
    db.add(submission)
    if is_correct:
        player.score += 1

    try:
        # The database uniqueness constraint is the final guard against concurrent duplicates.
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise BadRequestError("Bạn đã trả lời câu hỏi này rồi") from exc

    room = (
        db.query(Room)
        .options(selectinload(Room.players).joinedload(RoomPlayer.user))
        .filter(Room.id == room.id)
        .populate_existing()
        .first()
    )
    players_progress = _get_all_progress(db, room)
    # This response is returned only to the player who submitted the answer.
    return {
        "event": "answer_feedback",
        "room_code": room_code,
        "word_id": word_id,
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "players": players_progress,
    }


def public_progress_update(feedback: dict[str, Any], user_id: int) -> dict[str, Any]:
    """Remove answer-specific feedback before broadcasting to the whole room."""
    return {
        "event": "progress_update",
        "room_code": feedback["room_code"],
        "submitter": user_id,
        "players": feedback["players"],
    }


def _get_all_progress(db: Session, room: Room) -> list[dict[str, Any]]:
    counts = (
        db.query(
            Submission.user_id,
            func.count(Submission.id).label("total"),
            func.sum(case((Submission.is_correct.is_(True), 1), else_=0)).label("correct"),
        )
        .filter(Submission.room_id == room.id)
        .group_by(Submission.user_id)
        .all()
    )
    count_by_user = {
        user_id: {"correct": int(correct or 0), "total": int(total)}
        for user_id, total, correct in counts
    }
    result = []
    for player in room.players:
        data = count_by_user.get(player.user_id, {"correct": 0, "total": 0})
        result.append(
            {
                "user_id": player.user_id,
                "username": player.user.username if player.user else f"Player {player.user_id}",
                "correct": int(data.get("correct", 0)),
                "total": int(data.get("total", 0)),
                "score": player.score,
            }
        )
    return result


def finish_game(db: Session, room_code: str, user_id: int) -> dict[str, Any]:
    room = (
        db.query(Room)
        .filter(Room.code == room_code)
        .with_for_update()
        .populate_existing()
        .first()
    )
    if not room:
        raise NotFoundError("Không tìm thấy phòng")
    if room.host_id != user_id:
        raise ForbiddenError("Chỉ chủ phòng mới có thể kết thúc trận đấu")
    if room.status == "waiting":
        raise BadRequestError("Trận đấu chưa bắt đầu")
    if room.status != "finished":
        room.status = "finished"
        room.finished_at = datetime.utcnow()
        db.commit()

    room = (
        db.query(Room)
        .options(joinedload(Room.players).joinedload(RoomPlayer.user))
        .filter(Room.code == room_code)
        .populate_existing()
        .first()
    )
    payload = _finish_payload(room)
    return payload
