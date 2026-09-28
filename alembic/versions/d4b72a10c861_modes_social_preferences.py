"""Add independent game modes, board games, social features and preferences.

Revision ID: d4b72a10c861
Revises: a63f9d7b2c10
"""

from alembic import op
import sqlalchemy as sa


revision = "d4b72a10c861"
down_revision = "a63f9d7b2c10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("rooms", sa.Column("game_mode", sa.String(length=32), server_default="classic", nullable=False))
    op.add_column("rooms", sa.Column("board_game_mode", sa.String(length=32), nullable=True))
    op.add_column("rooms", sa.Column("board_state", sa.JSON(), nullable=True))
    op.add_column("solo_sessions", sa.Column("game_mode", sa.String(length=32), server_default="classic", nullable=False))
    op.add_column("users", sa.Column("avatar_key", sa.String(length=32), server_default="spark", nullable=False))
    op.add_column("users", sa.Column("preferences", sa.JSON(), server_default="{}", nullable=False))
    op.create_table(
        "friend_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("requester_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipient_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("requester_id", "recipient_id", name="uq_friend_request_pair"),
    )
    op.create_index("ix_friend_requests_requester_id", "friend_requests", ["requester_id"])
    op.create_index("ix_friend_requests_recipient_id", "friend_requests", ["recipient_id"])
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipient_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notification_type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("body", sa.String(length=500), server_default="", nullable=False),
        sa.Column("payload", sa.JSON(), server_default="{}", nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_notifications_recipient_id", "notifications", ["recipient_id"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])


def downgrade() -> None:
    op.drop_index("ix_notifications_is_read", table_name="notifications")
    op.drop_index("ix_notifications_recipient_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_friend_requests_recipient_id", table_name="friend_requests")
    op.drop_index("ix_friend_requests_requester_id", table_name="friend_requests")
    op.drop_table("friend_requests")
    op.drop_column("users", "preferences")
    op.drop_column("users", "avatar_key")
    op.drop_column("solo_sessions", "game_mode")
    op.drop_column("rooms", "board_state")
    op.drop_column("rooms", "board_game_mode")
    op.drop_column("rooms", "game_mode")
