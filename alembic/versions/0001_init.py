"""init

Revision ID: 0001_init
Revises: 
Create Date: 2026-05-04
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "prompts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("template", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_prompts_name", "prompts", ["name"], unique=False)
    op.create_index("ix_prompts_version", "prompts", ["version"], unique=False)

    op.create_table(
        "evaluations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("prompt_id", sa.String(length=36), sa.ForeignKey("prompts.id"), nullable=False),
        sa.Column("dataset_name", sa.String(length=255), nullable=False),
        sa.Column("model", sa.String(length=255), nullable=False),
        sa.Column("criteria", sa.JSON(), nullable=False),
        sa.Column("summary", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("evaluations")
    op.drop_index("ix_prompts_version", table_name="prompts")
    op.drop_index("ix_prompts_name", table_name="prompts")
    op.drop_table("prompts")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
