from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False)  # Mã PIN phòng (vd: WDUEL1)
    host_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_set_id = Column(Integer, ForeignKey("word_sets.id"), nullable=False)
    status = Column(String(20), default="waiting", nullable=False)  # waiting, playing, finished
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    # Relationships
    host = relationship("User", back_populates="hosted_rooms", foreign_keys=[host_id])
    word_set = relationship("WordSet", back_populates="rooms")
    players = relationship("RoomPlayer", back_populates="room", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="room", cascade="all, delete-orphan")


class RoomPlayer(Base):
    __tablename__ = "room_players"
    __table_args__ = (UniqueConstraint("room_id", "user_id", name="uq_room_players_room_user"),)

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(
        Integer,
        ForeignKey("rooms.id", name="fk_room_players_room_id_rooms", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, default=0, nullable=False)  # Số câu đúng
    is_ready = Column(Boolean, default=False, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    room = relationship("Room", back_populates="players")
    user = relationship("User", back_populates="room_players")


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint("room_id", "user_id", "word_id", name="uq_submissions_room_user_word"),
    )

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(
        Integer,
        ForeignKey("rooms.id", name="fk_submissions_room_id_rooms", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    submitted_answer = Column(String(255), nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    room = relationship("Room", back_populates="submissions")
    user = relationship("User", back_populates="submissions")
    word = relationship("Word", back_populates="submissions")
