"""add content library tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-08 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── content_folders ─────────────────────────────────────────────────────
    op.create_table(
        "content_folders",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_scanned_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.UniqueConstraint("path", name="uq_content_folders_path"),
    )
    op.create_index("ix_content_folders_is_active", "content_folders", ["is_active"])

    # ─── content_files ───────────────────────────────────────────────────────
    op.create_table(
        "content_files",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("folder_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("file_type", sa.String(20), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=True),
        sa.Column("thumbnail_path", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["folder_id"], ["content_folders.id"],
            ondelete="CASCADE",
            name="fk_content_files_folder_id",
        ),
        sa.UniqueConstraint("file_path", name="uq_content_files_file_path"),
        sa.CheckConstraint(
            "file_type IN ('video', 'audio')",
            name="chk_content_files_type",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'analyzing', 'analyzed', 'matched', 'queued', 'posted', 'failed')",
            name="chk_content_files_status",
        ),
    )
    op.create_index("ix_content_files_folder_id", "content_files", ["folder_id"])
    op.create_index("ix_content_files_file_type", "content_files", ["file_type"])
    op.create_index("ix_content_files_status", "content_files", ["status"])
    op.create_index("ix_content_files_content_hash", "content_files", ["content_hash"])

    # ─── ai_analysis ─────────────────────────────────────────────────────────
    op.create_table(
        "ai_analysis",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("content_file_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scenes", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("objects", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("activities", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("emotions", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("genre", sa.String(100), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("keywords", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("target_audience", sa.Text(), nullable=True),
        sa.Column("viral_potential_score", sa.Integer(), nullable=True),
        sa.Column("raw_response", postgresql.JSONB(), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("model_used", sa.String(100), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["content_file_id"], ["content_files.id"],
            ondelete="CASCADE",
            name="fk_ai_analysis_content_file_id",
        ),
        sa.UniqueConstraint("content_file_id", name="uq_ai_analysis_content_file_id"),
    )
    op.create_index(
        "ix_ai_analysis_content_file_id", "ai_analysis", ["content_file_id"]
    )

    # ─── generated_content ───────────────────────────────────────────────────
    op.create_table(
        "generated_content",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("content_file_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("hook", sa.Text(), nullable=True),
        sa.Column("cta", sa.Text(), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("hashtags", postgresql.ARRAY(sa.Text()), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["content_file_id"], ["content_files.id"],
            ondelete="CASCADE",
            name="fk_generated_content_content_file_id",
        ),
        sa.CheckConstraint(
            "platform IN ('instagram', 'tiktok', 'youtube', 'x', 'threads', 'snapchat')",
            name="chk_generated_content_platform",
        ),
    )
    op.create_index(
        "ix_generated_content_content_file_id",
        "generated_content",
        ["content_file_id"],
    )
    op.create_index(
        "ix_generated_content_platform", "generated_content", ["platform"]
    )


def downgrade() -> None:
    op.drop_table("generated_content")
    op.drop_table("ai_analysis")
    op.drop_table("content_files")
    op.drop_table("content_folders")
