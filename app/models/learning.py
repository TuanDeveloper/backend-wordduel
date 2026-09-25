from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class SoloSession(Base):
    __tablename__ = "solo_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    word_set_id = Column(Integer, ForeignKey("word_sets.id", ondelete="SET NULL"), nullable=True)
    source = Column(String(20), nullable=False, default="word_set", server_default="word_set")
    word_count = Column(Integer, nullable=False)
    question_count = Column(Integer, nullable=False)
    time_per_question = Column(Integer, nullable=True)
    question_word_ids = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="playing", server_default="playing")
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="solo_sessions")
    submissions = relationship("SoloSubmission", back_populates="session", cascade="all, delete-orphan")


class SoloSubmission(Base):
    __tablename__ = "solo_submissions"
    __table_args__ = (UniqueConstraint("session_id", "question_index", name="uq_solo_submissions_session_question"),)

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("solo_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    word_id = Column(Integer, ForeignKey("words.id", ondelete="CASCADE"), nullable=False)
    question_index = Column(Integer, nullable=False)
    submitted_answer = Column(String(255), nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False, server_default="false")
    response_time_ms = Column(Integer, nullable=False, default=0, server_default="0")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())

    session = relationship("SoloSession", back_populates="submissions")
    word = relationship("Word")


class SavedWord(Base):
    __tablename__ = "saved_words"
    __table_args__ = (UniqueConstraint("user_id", "word_id", name="uq_saved_words_user_word"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    word_id = Column(Integer, ForeignKey("words.id", ondelete="CASCADE"), nullable=False, index=True)
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())

    user = relationship("User", back_populates="saved_words")
    word = relationship("Word", back_populates="saved_entries")
