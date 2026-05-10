"""allow incomplete resolution

Revision ID: 0002_allow_incomplete_resolution
Revises: 0001_initial_schema
Create Date: 2026-05-10
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_allow_incomplete_resolution"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("resolution") as batch_op:
        batch_op.alter_column(
            "action_taken",
            existing_type=sa.String(),
            nullable=True,
        )
        batch_op.alter_column(
            "action_result",
            existing_type=sa.String(),
            nullable=True,
        )
        batch_op.alter_column(
            "date",
            existing_type=sa.String(),
            nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("resolution") as batch_op:
        batch_op.alter_column(
            "date",
            existing_type=sa.String(),
            nullable=False,
        )
        batch_op.alter_column(
            "action_result",
            existing_type=sa.String(),
            nullable=False,
        )
        batch_op.alter_column(
            "action_taken",
            existing_type=sa.String(),
            nullable=False,
        )
