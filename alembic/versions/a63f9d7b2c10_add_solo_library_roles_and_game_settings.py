"""Add solo practice, saved words, admin roles, context and game settings.

Revision ID: a63f9d7b2c10
Revises: 943c0ad1f6e2
"""

from alembic import op
import sqlalchemy as sa


revision = "a63f9d7b2c10"
down_revision = "943c0ad1f6e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=20), server_default="user", nullable=False))
    op.add_column("users", sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False))
    op.add_column("word_sets", sa.Column("is_hidden", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column("words", sa.Column("context_sentence", sa.String(length=1000), nullable=True))

    op.add_column("rooms", sa.Column("word_count", sa.Integer(), nullable=True))
    op.add_column("rooms", sa.Column("time_per_question", sa.Integer(), nullable=True))
    op.add_column("rooms", sa.Column("question_count", sa.Integer(), nullable=True))
    op.add_column("rooms", sa.Column("question_word_ids", sa.JSON(), nullable=True))
    op.add_column("submissions", sa.Column("question_index", sa.Integer(), nullable=True))
    op.execute(
        """WITH ranked AS (
            SELECT id, ROW_NUMBER() OVER (PARTITION BY room_id, user_id ORDER BY created_at, id) - 1 AS question_index
            FROM submissions
        )
        UPDATE submissions AS s SET question_index = ranked.question_index
        FROM ranked WHERE ranked.id = s.id"""
    )
    op.alter_column("submissions", "question_index", nullable=False, server_default="0")
    op.drop_constraint("uq_submissions_room_user_word", "submissions", type_="unique")
    op.create_unique_constraint(
        "uq_submissions_room_user_question", "submissions", ["room_id", "user_id", "question_index"]
    )
    op.execute(
        """UPDATE rooms AS r
        SET word_count = counts.word_count,
            question_count = counts.word_count,
            time_per_question = 20,
            question_word_ids = COALESCE(counts.word_ids, '[]'::json)
        FROM (
            SELECT ws.id AS word_set_id, COUNT(w.id)::integer AS word_count,
                   json_agg(w.id ORDER BY w.id) FILTER (WHERE w.id IS NOT NULL) AS word_ids
            FROM word_sets AS ws LEFT JOIN words AS w ON w.word_set_id = ws.id
            GROUP BY ws.id
        ) AS counts
        WHERE counts.word_set_id = r.word_set_id"""
    )

    op.create_table(
        "solo_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("word_set_id", sa.Integer(), sa.ForeignKey("word_sets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source", sa.String(length=20), nullable=False, server_default="word_set"),
        sa.Column("word_count", sa.Integer(), nullable=False),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("time_per_question", sa.Integer(), nullable=True),
        sa.Column("question_word_ids", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="playing"),
        sa.Column("started_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_solo_sessions_user_id", "solo_sessions", ["user_id"])
    op.create_table(
        "solo_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("solo_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("word_id", sa.Integer(), sa.ForeignKey("words.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_index", sa.Integer(), nullable=False),
        sa.Column("submitted_answer", sa.String(length=255), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("response_time_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("session_id", "question_index", name="uq_solo_submissions_session_question"),
    )
    op.create_index("ix_solo_submissions_session_id", "solo_submissions", ["session_id"])
    op.create_table(
        "saved_words",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("word_id", sa.Integer(), sa.ForeignKey("words.id", ondelete="CASCADE"), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "word_id", name="uq_saved_words_user_word"),
    )
    op.create_index("ix_saved_words_user_id", "saved_words", ["user_id"])
    op.create_index("ix_saved_words_word_id", "saved_words", ["word_id"])


def downgrade() -> None:
    op.drop_index("ix_saved_words_word_id", table_name="saved_words")
    op.drop_index("ix_saved_words_user_id", table_name="saved_words")
    op.drop_table("saved_words")
    op.drop_index("ix_solo_submissions_session_id", table_name="solo_submissions")
    op.drop_table("solo_submissions")
    op.drop_index("ix_solo_sessions_user_id", table_name="solo_sessions")
    op.drop_table("solo_sessions")

    op.drop_constraint("uq_submissions_room_user_question", "submissions", type_="unique")
    op.create_unique_constraint(
        "uq_submissions_room_user_word", "submissions", ["room_id", "user_id", "word_id"]
    )
    op.drop_column("submissions", "question_index")
    op.drop_column("rooms", "question_word_ids")
    op.drop_column("rooms", "question_count")
    op.drop_column("rooms", "time_per_question")
    op.drop_column("rooms", "word_count")
    op.drop_column("words", "context_sentence")
    op.drop_column("word_sets", "is_hidden")
    op.drop_column("users", "is_active")
    op.drop_column("users", "role")
