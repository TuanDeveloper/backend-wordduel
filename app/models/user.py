from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(254), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user", server_default="user")
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    avatar_key = Column(String(32), nullable=False, default="spark", server_default="spark")
    preferences = Column(JSON, nullable=False, default=dict, server_default="{}")
    rating = Column(Integer, nullable=False, default=1000, server_default="1000")
    rated_games = Column(Integer, nullable=False, default=0, server_default="0")
    wins = Column(Integer, nullable=False, default=0, server_default="0")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    word_sets = relationship("WordSet", back_populates="creator")
    hosted_rooms = relationship("Room", back_populates="host", foreign_keys="Room.host_id")
    room_players = relationship("RoomPlayer", back_populates="user")
    submissions = relationship("Submission", back_populates="user")
    solo_sessions = relationship("SoloSession", back_populates="user", cascade="all, delete-orphan")
    saved_words = relationship("SavedWord", back_populates="user", cascade="all, delete-orphan")
