from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, text

from app.db.base import Base


class MatchmakingEntry(Base):
    __tablename__ = "matchmaking_entries"
    __table_args__ = (
        Index(
            "uq_matchmaking_searching_user",
            "user_id",
            unique=True,
            postgresql_where=text("status = 'searching'"),
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    game_mode = Column(String(32), nullable=False)
    board_game_mode = Column(String(32), nullable=True)
    status = Column(String(20), nullable=False, default="searching")
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    matched_at = Column(DateTime, nullable=True)
