from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class WordSet(Base):
    __tablename__ = "word_sets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255))
    creator_id = Column(Integer, ForeignKey("users.id"))
    is_hidden = Column(Boolean, nullable=False, default=False, server_default="false")

    creator = relationship("User", back_populates="word_sets")
    words = relationship("Word", back_populates="word_set", cascade="all, delete-orphan")
    rooms = relationship("Room", back_populates="word_set")


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word_set_id = Column(Integer, ForeignKey("word_sets.id"))
    term = Column(String(100), nullable=False)  # Từ tiếng Anh
    definition = Column(String(255), nullable=False)  # Nghĩa
    example = Column(String(500))  # Câu ví dụ
    context_sentence = Column(String(1000), nullable=True)

    word_set = relationship("WordSet", back_populates="words")
    submissions = relationship("Submission", back_populates="word")
    saved_entries = relationship("SavedWord", back_populates="word", cascade="all, delete-orphan")
