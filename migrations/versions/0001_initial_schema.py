"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-09
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "monitor",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("interval_seconds", sa.Integer(), nullable=False),
        sa.Column("last_checked_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "httpmonitorconfig",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("expected_status", sa.Integer(), nullable=False),
        sa.Column("monitor_id", sa.Integer(), sa.ForeignKey("monitor.id"), unique=True),
    )
    op.create_table(
        "incident",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("monitor_id", sa.Integer(), sa.ForeignKey("monitor.id"), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("service", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("summary", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
    )
    op.create_table(
        "trigger",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("expected_status", sa.Integer(), nullable=False),
        sa.Column("observed_status", sa.Integer(), nullable=True),
        sa.Column("failed_attempts", sa.Integer(), nullable=False),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incident.id"), unique=True),
    )
    op.create_table(
        "evidence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("response_time_in_ms", sa.Integer(), nullable=True),
        sa.Column("last_cpu_usage_percent", sa.Float(), nullable=False),
        sa.Column("last_memory_usage_percent", sa.Float(), nullable=False),
        sa.Column("error_message", sa.String(), nullable=False),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incident.id"), unique=True),
    )
    op.create_table(
        "resolution",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("action_taken", sa.String(), nullable=False),
        sa.Column("action_result", sa.String(), nullable=False),
        sa.Column("date", sa.String(), nullable=False),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incident.id"), unique=True),
    )


def downgrade() -> None:
    op.drop_table("resolution")
    op.drop_table("evidence")
    op.drop_table("trigger")
    op.drop_table("incident")
    op.drop_table("httpmonitorconfig")
    op.drop_table("monitor")
