"""Allow rooms to combine word sets and configure answer scoring.

Revision ID: e8c41b27d935
Revises: d4b72a10c861
"""

from alembic import op
import sqlalchemy as sa


revision = "e8c41b27d935"
down_revision = "d4b72a10c861"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("rooms", sa.Column("word_set_ids", sa.JSON(), nullable=True))
    op.add_column("rooms", sa.Column("points_per_correct", sa.Integer(), server_default="1", nullable=False))
    op.execute("UPDATE rooms SET word_set_ids = json_build_array(word_set_id)")


def downgrade() -> None:
    op.drop_column("rooms", "points_per_correct")
    op.drop_column("rooms", "word_set_ids")
