"""Add persisted matchmaking queue."""

from alembic import op
import sqlalchemy as sa


revision = "f3a91c8d2b70"
down_revision = "e8c41b27d935"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "matchmaking_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("game_mode", sa.String(length=32), nullable=False),
        sa.Column("board_game_mode", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="searching"),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("matched_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "uq_matchmaking_searching_user",
        "matchmaking_entries",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("status = 'searching'"),
    )
    op.create_index("ix_matchmaking_mode_status", "matchmaking_entries", ["status", "game_mode", "board_game_mode"])


def downgrade() -> None:
    op.drop_index("ix_matchmaking_mode_status", table_name="matchmaking_entries")
    op.drop_index("uq_matchmaking_searching_user", table_name="matchmaking_entries")
    op.drop_table("matchmaking_entries")
