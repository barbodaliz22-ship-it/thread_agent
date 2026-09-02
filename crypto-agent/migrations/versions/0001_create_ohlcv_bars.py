"""create ohlcv_bars table

Revision ID: 0001_create_ohlcv_bars
Revises:
Create Date: 2026-09-02

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_create_ohlcv_bars"
down_revision: str | None = None
branch_labels: Sequence[str] | str | None = None
depends_on: Sequence[str] | str | None = None

quality_status_enum = postgresql.ENUM(
    "ok", "stale", "missing_fields", "duplicate", "impossible_value", "source_error",
    name="dataqualitystatus",
)
timeframe_enum = postgresql.ENUM(
    "1m", "5m", "15m", "1h", "4h", "1d",
    name="timeframe",
)


def upgrade() -> None:
    bind = op.get_bind()
    quality_status_enum.create(bind, checkfirst=True)
    timeframe_enum.create(bind, checkfirst=True)

    op.create_table(
        "ohlcv_bars",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("asset", sa.String(length=32), nullable=False),
        sa.Column("timeframe", timeframe_enum, nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("open", sa.Numeric(24, 8), nullable=False),
        sa.Column("high", sa.Numeric(24, 8), nullable=False),
        sa.Column("low", sa.Numeric(24, 8), nullable=False),
        sa.Column("close", sa.Numeric(24, 8), nullable=False),
        sa.Column("volume", sa.Numeric(32, 8), nullable=False),
        sa.Column("quality_status", quality_status_enum, nullable=False),
        sa.UniqueConstraint(
            "source", "asset", "timeframe", "timestamp", name="uq_ohlcv_source_asset_tf_ts"
        ),
    )
    op.create_index(
        "ix_ohlcv_asset_timeframe_timestamp",
        "ohlcv_bars",
        ["asset", "timeframe", "timestamp"],
    )


def downgrade() -> None:
    op.drop_index("ix_ohlcv_asset_timeframe_timestamp", table_name="ohlcv_bars")
    op.drop_table("ohlcv_bars")
    quality_status_enum.drop(op.get_bind(), checkfirst=True)
    timeframe_enum.drop(op.get_bind(), checkfirst=True)
