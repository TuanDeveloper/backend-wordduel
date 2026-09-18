from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    word_sets = relationship("WordSet", back_populates="creator")
    hosted_rooms = relationship("Room", back_populates="host", foreign_keys="Room.host_id")
    room_players = relationship("RoomPlayer", back_populates="user")
    submissions = relationship("Submission", back_populates="user")
