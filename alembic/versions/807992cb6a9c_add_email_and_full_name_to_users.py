"""Add email and full_name to users."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "807992cb6a9c"
down_revision: Union[str, Sequence[str], None] = "c1a4d8e9f2b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Preserve the cascade behavior while giving these constraints stable names.
    op.drop_constraint("room_players_room_id_fkey", "room_players", type_="foreignkey")
    op.create_foreign_key(
        "fk_room_players_room_id_rooms", "room_players", "rooms", ["room_id"], ["id"], ondelete="CASCADE"
    )
    op.drop_constraint("submissions_room_id_fkey", "submissions", type_="foreignkey")
    op.create_foreign_key(
        "fk_submissions_room_id_rooms", "submissions", "rooms", ["room_id"], ["id"], ondelete="CASCADE"
    )

    op.add_column("users", sa.Column("email", sa.String(length=254), nullable=True))
    op.add_column("users", sa.Column("full_name", sa.String(length=100), nullable=True))
    op.execute(
        "UPDATE users "
        "SET email = 'legacy-user-' || id::text || '@example.com', full_name = username "
        "WHERE email IS NULL OR full_name IS NULL"
    )
    op.alter_column("users", "email", existing_type=sa.String(length=254), nullable=False)
    op.alter_column("users", "full_name", existing_type=sa.String(length=100), nullable=False)
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")
    op.drop_column("users", "full_name")
    op.drop_column("users", "email")

    op.drop_constraint("fk_submissions_room_id_rooms", "submissions", type_="foreignkey")
    op.create_foreign_key(
        "submissions_room_id_fkey", "submissions", "rooms", ["room_id"], ["id"], ondelete="CASCADE"
    )
    op.drop_constraint("fk_room_players_room_id_rooms", "room_players", type_="foreignkey")
    op.create_foreign_key(
        "room_players_room_id_fkey", "room_players", "rooms", ["room_id"], ["id"], ondelete="CASCADE"
    )
