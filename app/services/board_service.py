"""Turn-based board game rules layered on a room's existing word set."""

import random
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.room import Room, RoomPlayer
from app.models.word import Word
from app.services.game_service import _grade_answer, _public_question


def _players(room: Room) -> list[RoomPlayer]:
    return sorted(room.players, key=lambda player: (player.joined_at or datetime.min, player.id))


def _board_payload(db: Session, room: Room) -> dict[str, Any]:
    state = room.board_state or {}
    public_state = dict(state)
    defense_answers = public_state.pop("defense_answers", {})
    public_state["defense_answered_count"] = len(defense_answers)
    player_rows = _players(room)
    user_ids = [player.user_id for player in player_rows]
    question_ids = room.question_word_ids or []
    cursor = int(state.get("question_cursor", 0))
    question = None
    phase = state.get("phase", "question")
    if question_ids:
        word_id = question_ids[cursor % len(question_ids)]
        word = db.query(Word).filter(Word.id == word_id).first()
        if word:
            pool = db.query(Word.term).filter(Word.word_set_id.in_(room.word_set_ids or [room.word_set_id]), Word.id != word.id).all()
            question = _public_question(word, room.game_mode, [row[0] for row in pool])
    return {
        "event": "board_game_started" if room.status == "playing" else "board_game_finished",
        "room_code": room.code,
        "game_mode": room.game_mode,
        "board_game_mode": room.board_game_mode,
        "time_per_question": room.time_per_question,
        "total_words": len(question_ids),
        "board": {
            **public_state,
            "players": [
                {
                    "user_id": player.user_id,
                    "username": player.user.username if player.user else f"Player {player.user_id}",
                    "score": player.score,
                    "position": (state.get("positions") or {}).get(str(player.user_id), 0),
                    "cash": (state.get("cash") or {}).get(str(player.user_id), 0),
                }
                for player in player_rows
            ],
            "active_user_id": None if phase == "defense" else (user_ids[int(state.get("turn_index", 0)) % len(user_ids)] if user_ids else None),
            "phase": phase,
            "question": question,
        },
    }


def start_board_game(db: Session, room: Room, players: list[RoomPlayer]) -> dict[str, Any]:
    if len(players) < 2:
        raise BadRequestError("Board game cần ít nhất hai người chơi")
    if any(not player.is_ready for player in players):
        raise BadRequestError("Tất cả người chơi cần sẵn sàng trước khi bắt đầu")
    words = db.query(Word).filter(Word.word_set_id.in_(room.word_set_ids or [room.word_set_id])).order_by(Word.id).all()
    if not words:
        raise BadRequestError("Bộ từ vựng này chưa có từ nào")
    selected = random.sample(words, min(room.word_count or len(words), len(words), 500))
    count = room.question_count or max(20, len(selected))
    ids: list[int] = []
    while len(ids) < count:
        ids.extend(word.id for word in random.sample(selected, len(selected)))
    ids = ids[:count]
    user_ids = [player.user_id for player in _players(room)]
    room.word_count = len(selected)
    room.question_count = count
    room.question_word_ids = ids
    room.board_state = {
        "phase": "question",
        "turn_index": 0,
        "round": 1,
        "question_cursor": 0,
        "positions": {str(user_id): 0 for user_id in user_ids},
        "cash": {str(user_id): 20 for user_id in user_ids},
        "properties": {},
        "territories": {},
        "boss_hp": 100,
        "party_hearts": 3,
        "defense_answers": {},
        "pending_tile": None,
        "last_event": None,
    }
    room.status = "playing"
    db.commit()
    db.refresh(room)
    return _board_payload(db, room)


def get_board_state(db: Session, room: Room, user_id: int) -> dict[str, Any]:
    if not any(player.user_id == user_id for player in room.players):
        raise ForbiddenError("Bạn không phải thành viên của phòng")
    return _board_payload(db, room)


def _finish_if_needed(db: Session, room: Room, state: dict[str, Any], player_rows: list[RoomPlayer]) -> None:
    mode = room.board_game_mode
    finished = (
        (mode == "race" and max(state["positions"].values(), default=0) >= 24)
        or (mode == "boss" and (state["boss_hp"] <= 0 or state["party_hearts"] <= 0))
        or (mode == "territory" and state["round"] > 8)
        or (mode == "monopoly" and state["round"] > 10)
    )
    if finished:
        room.status = "finished"
        room.finished_at = datetime.utcnow()
        if mode == "territory":
            for player in player_rows:
                player.score = sum(1 for owner in state["territories"].values() if owner == player.user_id)
        elif mode == "monopoly":
            for player in player_rows:
                player.score = state["cash"].get(str(player.user_id), 0) + 5 * sum(
                    1 for owner in state["properties"].values() if owner == player.user_id
                )
        from app.services.ranking_service import apply_room_result

        apply_room_result(db, room, player_rows)


def board_action(db: Session, room_code: str, user_id: int, action: str, answer: str | None = None) -> dict[str, Any]:
    room = (
        db.query(Room)
        # Keep FOR UPDATE on the room row only. joinedload emits outer joins for
        # the optional player/user relationships, which PostgreSQL cannot lock.
        .options(selectinload(Room.players).selectinload(RoomPlayer.user))
        .filter(Room.code == room_code)
        .with_for_update()
        .populate_existing()
        .first()
    )
    if not room:
        raise NotFoundError("Không tìm thấy phòng")
    if room.status != "playing" or not room.board_game_mode:
        raise BadRequestError("Board game chưa bắt đầu hoặc đã kết thúc")
    player_rows = _players(room)
    user_ids = [player.user_id for player in player_rows]
    if user_id not in user_ids:
        raise ForbiddenError("Bạn không phải thành viên của phòng")
    state = dict(room.board_state or {})
    turn_index = int(state.get("turn_index", 0)) % len(user_ids)
    active_user_id = user_ids[turn_index]
    mode = room.board_game_mode
    phase = state.get("phase", "question")

    if mode == "boss" and phase == "defense":
        if action != "answer" or answer is None:
            raise BadRequestError("Hãy trả lời câu hỏi phản công để né đòn")
        if str(user_id) in state["defense_answers"]:
            raise BadRequestError("Bạn đã trả lời lượt phản công này")
        cursor = int(state["question_cursor"]) % len(room.question_word_ids)
        word = db.query(Word).filter(Word.id == room.question_word_ids[cursor]).first()
        correct, near, _expected = _grade_answer(room.game_mode, word, answer)
        if near:
            return {**_board_payload(db, room), "event": "board_state_update", "feedback": {"is_correct": False, "near_match": True, "retryable": True}}
        state["defense_answers"][str(user_id)] = correct
        if len(state["defense_answers"]) == len(user_ids):
            avoided = all(state["defense_answers"].values())
            if not avoided:
                state["party_hearts"] = max(0, state["party_hearts"] - 1)
            state["last_event"] = "Phòng né được đòn phản công!" if avoided else "Boss phản công, đội mất một mạng."
            state["defense_answers"] = {}
            state["phase"] = "question"
            state["turn_index"] = 0
            state["round"] += 1
            state["question_cursor"] += 1
        _finish_if_needed(db, room, state, player_rows)
        room.board_state = state
        db.commit()
        if room.status == "finished":
            from app.services.game_service import _finish_payload

            return {**_finish_payload(room, db), "board_game_mode": room.board_game_mode}
        return {**_board_payload(db, room), "event": "board_state_update", "feedback": {"is_correct": correct, "near_match": near}}

    if active_user_id != user_id:
        raise ForbiddenError("Hãy đợi đến lượt của bạn")
    if mode == "monopoly" and action == "roll":
        if state.get("pending_tile") is not None:
            raise BadRequestError("Hãy trả lời câu hỏi trên ô hiện tại trước")
        dice = random.randint(1, 6)
        position = (int(state["positions"].get(str(user_id), 0)) + dice) % 20
        state["positions"][str(user_id)] = position
        state["pending_tile"] = position
        event = None
        if position in (4, 9, 14, 19):
            event = random.choice(["Nhặt được 3 xu cơ hội!", "Nộp 2 xu phí đường!", "Ô may mắn: nhận thêm lượt."])
            state["cash"][str(user_id)] += 3 if "Nhặt" in event else -2 if "Nộp" in event else 0
            if "thêm lượt" in event:
                state["bonus_turn"] = True
            if event:
                # Chance spaces resolve immediately; they do not own a question
                # or a property, so advance the turn without leaving a pending tile.
                state["pending_tile"] = None
                if state.pop("bonus_turn", False):
                    wrapped = False
                else:
                    next_index = (turn_index + 1) % len(user_ids)
                    state["turn_index"] = next_index
                    wrapped = next_index == 0
                if wrapped:
                    state["round"] += 1
                    _finish_if_needed(db, room, state, player_rows)
        state["last_event"] = f"{player_rows[turn_index].user.username} tung được {dice}, đến ô {position + 1}." + (f" {event}" if event else "")
        room.board_state = state
        db.commit()
        if room.status == "finished":
            from app.services.game_service import _finish_payload

            return {**_finish_payload(room, db), "board_game_mode": room.board_game_mode}
        return {**_board_payload(db, room), "event": "board_state_update", "dice": dice}
    if action != "answer" or answer is None:
        raise BadRequestError("Gửi đáp án cho câu hỏi hiện tại")

    cursor = int(state.get("question_cursor", 0)) % len(room.question_word_ids)
    word_id = room.question_word_ids[cursor]
    word = db.query(Word).filter(Word.id == word_id).first()
    correct, near_match, expected = _grade_answer(room.game_mode, word, answer)
    if near_match:
        return {**_board_payload(db, room), "event": "board_state_update", "feedback": {"is_correct": False, "near_match": True, "retryable": True, "correct_answer": expected}}
    current_player = next(player for player in player_rows if player.user_id == user_id)
    if correct:
        current_player.score += room.points_per_correct or 0
    if mode == "monopoly":
        tile = state.pop("pending_tile", None)
        tile_key = str(tile)
        owner_id = state["properties"].get(tile_key)
        if correct and owner_id is None:
            state["properties"][tile_key] = user_id
            state["cash"][str(user_id)] -= 2
            state["last_event"] = f"Đáp án đúng! Bạn sở hữu ô {tile + 1}."
        elif correct and owner_id and owner_id != user_id:
            state["cash"][str(user_id)] -= 3
            state["cash"][str(owner_id)] = state["cash"].get(str(owner_id), 20) + 3
            state["last_event"] = "Đáp án đúng, bạn trả 3 xu phí đi qua ô đối thủ."
        else:
            state["last_event"] = "Chưa đúng; ô này vẫn còn trống." if not owner_id else "Chưa đúng; bạn bỏ lỡ quyền sở hữu ô."
    elif mode == "race":
        position = int(state["positions"].get(str(user_id), 0))
        if correct:
            position += 2 if cursor % 6 == 0 else 1
            if position % 7 == 0:
                position += 1
            state["last_event"] = "Đúng! Bạn tiến nhanh thêm một ô." if position % 7 == 1 else "Đúng! Quân đua tiến lên."
        else:
            position = max(0, position - (2 if cursor % 5 == 0 else 1))
            state["last_event"] = "Sai đáp án, bạn trượt lùi trên đường đua."
        state["positions"][str(user_id)] = min(24, position)
    elif mode == "territory":
        tile = str(cursor % 16)
        previous_owner = state["territories"].get(tile)
        if correct:
            state["territories"][tile] = user_id
            state["last_event"] = "Bạn chiếm một vùng mới!" if previous_owner != user_id else "Bạn củng cố vùng đang giữ."
        else:
            state["last_event"] = "Sai đáp án, vùng này chưa được chiếm."
    else:
        if correct:
            state["boss_hp"] = max(0, state["boss_hp"] - 15)
            state["last_event"] = "Đòn đánh trúng Boss!"
        else:
            state["last_event"] = "Boss đỡ được đòn đánh."

    if state.pop("bonus_turn", False):
        next_index = turn_index
        wrapped = False
    else:
        next_index = (turn_index + 1) % len(user_ids)
        wrapped = next_index == 0
    state["turn_index"] = next_index
    state["question_cursor"] = cursor + 1
    if wrapped:
        if mode == "boss" and state["boss_hp"] > 0:
            state["phase"] = "defense"
            state["last_event"] = "Boss đang phản công: cả đội hãy trả lời!"
        else:
            state["round"] += 1
    _finish_if_needed(db, room, state, player_rows)
    room.board_state = state
    db.commit()
    if room.status == "finished":
        from app.services.game_service import _finish_payload

        return {**_finish_payload(room, db), "board_game_mode": room.board_game_mode}
    return {
        **_board_payload(db, room),
        "event": "board_state_update",
        "feedback": {"is_correct": correct, "near_match": near_match, "correct_answer": expected},
    }
