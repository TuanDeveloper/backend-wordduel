import json
import random
from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.learning import SavedWord, SoloSession, SoloSubmission
from app.models.user import User
from app.models.word import Word, WordSet
from app.schemas.response import ResponseSchema
from app.schemas.room import SoloStartRequest, SoloSubmitRequest
from app.services.game_service import _mask_context

router = APIRouter(prefix="/solo", tags=["solo"])


def _get_session(db: Session, session_id: int, user_id: int) -> SoloSession:
    session = db.query(SoloSession).filter(SoloSession.id == session_id).first()
    if not session:
        raise NotFoundError("Không tìm thấy buổi luyện tập")
    if session.user_id != user_id:
        raise ForbiddenError("Buổi luyện tập này không thuộc về bạn")
    return session


def _session_state(db: Session, session: SoloSession) -> dict:
    question_word_ids = json.loads(session.question_word_ids)
    words_by_id = {
        word.id: word
        for word in db.query(Word).filter(Word.id.in_(set(question_word_ids))).all()
    }
    words = [
        {
            "id": words_by_id[word_id].id,
            "definition": words_by_id[word_id].definition,
            "context_sentence": _mask_context(
                words_by_id[word_id].context_sentence, words_by_id[word_id].term
            ),
        }
        for word_id in question_word_ids
        if word_id in words_by_id
    ]
    answers = db.query(SoloSubmission).filter(SoloSubmission.session_id == session.id).order_by(SoloSubmission.question_index).all()
    correct_count = sum(1 for answer in answers if answer.is_correct)
    average_response_time_ms = round(sum(answer.response_time_ms for answer in answers) / len(answers)) if answers else 0
    return {
        "event": "solo_finished" if session.status == "completed" else "solo_started",
        "session_id": session.id,
        "source": session.source,
        "word_set_id": session.word_set_id,
        "word_count": session.word_count,
        "question_count": session.question_count,
        "time_per_question": session.time_per_question,
        "words": words,
        "answers": [
            {
                "question_index": answer.question_index,
                "word_id": answer.word_id,
                "user_answer": answer.submitted_answer,
                "is_correct": answer.is_correct,
                "response_time_ms": answer.response_time_ms,
                "correct_answer": answer.word.term if answer.word else "",
            }
            for answer in answers
        ],
        "correct_count": correct_count,
        "average_response_time_ms": average_response_time_ms,
        "wrong_word_ids": list({answer.word_id for answer in answers if not answer.is_correct}),
        "status": session.status,
    }


@router.post("/start", response_model=ResponseSchema[dict], status_code=status.HTTP_201_CREATED)
def start_solo(
    request: SoloStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    if request.source == "library":
        pool = (
            db.query(Word)
            .join(SavedWord, SavedWord.word_id == Word.id)
            .join(WordSet, WordSet.id == Word.word_set_id)
            .filter(SavedWord.user_id == current_user.id, WordSet.is_hidden.is_(False))
            .order_by(SavedWord.created_at.desc())
            .all()
        )
        word_set_id = None
    else:
        if not request.word_set_id:
            raise BadRequestError("Vui lòng chọn bộ từ vựng")
        word_set = db.query(WordSet).filter(
            WordSet.id == request.word_set_id,
            WordSet.is_hidden.is_(False),
        ).first()
        if not word_set:
            raise NotFoundError("Không tìm thấy bộ từ vựng")
        pool = db.query(Word).filter(Word.word_set_id == word_set.id).order_by(Word.id).all()
        word_set_id = word_set.id

    if not pool:
        raise BadRequestError("Nguồn luyện tập chưa có từ vựng")
    selected = random.sample(pool, min(request.word_count or len(pool), len(pool), 500))
    question_count = request.question_count or len(selected)
    question_ids: list[int] = []
    selected_ids = [word.id for word in selected]
    while len(question_ids) < question_count:
        question_ids.extend(random.sample(selected_ids, len(selected_ids)))
    question_ids = question_ids[:question_count]

    session = SoloSession(
        user_id=current_user.id,
        word_set_id=word_set_id,
        source=request.source,
        word_count=len(selected_ids),
        question_count=question_count,
        time_per_question=request.time_per_question,
        question_word_ids=json.dumps(question_ids),
        status="playing",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return ResponseSchema(data=_session_state(db, session), message="Bắt đầu luyện tập")


@router.get("/{session_id}", response_model=ResponseSchema[dict])
def get_solo_state(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    session = _get_session(db, session_id, current_user.id)
    return ResponseSchema(data=_session_state(db, session), message="Tải trạng thái luyện tập")


@router.post("/{session_id}/submit", response_model=ResponseSchema[dict])
def submit_solo_answer(
    session_id: int,
    request: SoloSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema[dict]:
    session = db.query(SoloSession).filter(SoloSession.id == session_id).with_for_update().first()
    if not session:
        raise NotFoundError("Không tìm thấy buổi luyện tập")
    if session.user_id != current_user.id:
        raise ForbiddenError("Buổi luyện tập này không thuộc về bạn")
    if session.status != "playing":
        raise BadRequestError("Buổi luyện tập đã kết thúc")
    word_ids = json.loads(session.question_word_ids)
    if request.question_index >= len(word_ids) or word_ids[request.question_index] != request.word_id:
        raise BadRequestError("Câu hỏi không nằm trong buổi luyện tập")
    word = db.query(Word).filter(Word.id == request.word_id).first()
    if not word:
        raise NotFoundError("Từ vựng không còn tồn tại")
    correct = request.submitted_answer.strip().casefold() == word.term.strip().casefold()
    answer = SoloSubmission(
        session_id=session.id,
        word_id=word.id,
        question_index=request.question_index,
        submitted_answer=request.submitted_answer.strip(),
        is_correct=correct,
        response_time_ms=request.response_time_ms,
    )
    db.add(answer)
    try:
        db.flush()
        answered_count = db.query(SoloSubmission.id).filter(SoloSubmission.session_id == session.id).count()
        if answered_count == session.question_count:
            session.status = "completed"
            session.finished_at = datetime.utcnow()
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise BadRequestError("Câu hỏi này đã được trả lời") from exc

    return ResponseSchema(
        data={
            "event": "answer_feedback",
            "session_id": session.id,
            "question_index": request.question_index,
            "word_id": word.id,
            "user_answer": answer.submitted_answer,
            "is_correct": correct,
            "correct_answer": word.term,
            "response_time_ms": answer.response_time_ms,
            "state": _session_state(db, session),
        },
        message="Đã chấm câu trả lời",
    )
