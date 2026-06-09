"""refactor schema: add users, drop devices/ai/scanner tables, expand platforms

Revision ID: 0003
Revises: 0001
Create Date: 2026-06-08 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Drop AI/scanner tables (may not exist if 0002 was never applied) ──────
    op.execute("DROP TABLE IF EXISTS generated_content CASCADE")
    op.execute("DROP TABLE IF EXISTS ai_analysis CASCADE")
    op.execute("DROP TABLE IF EXISTS content_files CASCADE")
    op.execute("DROP TABLE IF EXISTS content_folders CASCADE")

    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # ── uploads: add user_id + content columns ────────────────────────────────
    op.add_column("uploads", sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("uploads", sa.Column("title", sa.String(500), nullable=True))
    op.add_column("uploads", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("uploads", sa.Column("hashtags", postgresql.ARRAY(sa.String()), nullable=True))
    # duration_seconds: widen Integer → Float
    op.alter_column("uploads", "duration_seconds", type_=sa.Float(), nullable=True)

    # Assign all existing uploads to the first user (none exist in practice)
    op.create_foreign_key(
        "fk_uploads_user_id",
        "uploads", "users",
        ["user_id"], ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_uploads_user_id", "uploads", ["user_id"])

    # ── social_accounts: migrate device_id → user_id, expand platform list ────
    # 1. Add new user_id column
    op.add_column(
        "social_accounts",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 2. Drop old constraints that reference device_id
    op.drop_constraint("uq_social_accounts_device_platform", "social_accounts", type_="unique")
    op.drop_constraint("chk_social_accounts_platform", "social_accounts", type_="check")
    op.drop_constraint("fk_social_accounts_device_id", "social_accounts", type_="foreignkey")
    op.drop_index("ix_social_accounts_device_id", "social_accounts")

    # Remove any rows with platforms not in the new enum
    op.execute(
        "DELETE FROM social_accounts WHERE platform NOT IN "
        "('instagram', 'youtube', 'tiktok', 'x', 'threads', 'snapchat')"
    )

    # 3. Drop old column
    op.drop_column("social_accounts", "device_id")

    # 4. Add new constraints
    op.create_check_constraint(
        "chk_social_accounts_platform",
        "social_accounts",
        "platform IN ('instagram', 'youtube', 'tiktok', 'x', 'threads', 'snapchat')",
    )
    op.create_unique_constraint(
        "uq_social_accounts_user_platform_pid",
        "social_accounts",
        ["user_id", "platform", "platform_user_id"],
    )
    op.create_foreign_key(
        "fk_social_accounts_user_id",
        "social_accounts", "users",
        ["user_id"], ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_social_accounts_user_id", "social_accounts", ["user_id"])

    # ── posts: drop caption column (now on upload) ────────────────────────────
    # Keep caption for per-account override flexibility — leave it

    # ── devices table: drop (replaced by users) ───────────────────────────────
    # Posts and uploads no longer reference devices directly; safe to drop
    op.execute("DROP TABLE IF EXISTS devices CASCADE")


def downgrade() -> None:
    # Recreate devices
    op.create_table(
        "devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("meta", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    # Restoring full state is complex; mark as non-trivial downgrade
    raise NotImplementedError("Downgrade from 0003 requires manual intervention.")
