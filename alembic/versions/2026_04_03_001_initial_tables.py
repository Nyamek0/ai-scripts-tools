"""Création des tables users, jobs, module_stats

Revision ID: 001
Revises: None
Create Date: 2026-04-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Table users ───────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_superadmin", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )

    # ── Table jobs ────────────────────────────────────────────────────────
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"),
                  nullable=True, index=True),
        sa.Column("module_name", sa.String(100), nullable=False, index=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending",
                  index=True),
        sa.Column("input_filename", sa.String(500), nullable=True),
        sa.Column("input_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("result_url", sa.String(1000), nullable=True),
        sa.Column("output_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── Table module_stats ────────────────────────────────────────────────
    op.create_table(
        "module_stats",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("module_name", sa.String(100), unique=True, nullable=False,
                  index=True),
        sa.Column("total_jobs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("successful_jobs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_jobs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_processing_time_ms", sa.BigInteger(), nullable=False,
                  server_default="0"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("module_stats")
    op.drop_table("jobs")
    op.drop_table("users")
