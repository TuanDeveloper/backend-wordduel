"""Persist ELO rating and once-only room rating updates."""

from alembic import op
import sqlalchemy as sa


revision = "b7d24f91c603"
down_revision = "f3a91c8d2b70"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("rating", sa.Integer(), nullable=False, server_default="1000"))
    op.add_column("users", sa.Column("rated_games", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("wins", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("rooms", sa.Column("rating_applied", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("rooms", "rating_applied")
    op.drop_column("users", "wins")
    op.drop_column("users", "rated_games")
    op.drop_column("users", "rating")
