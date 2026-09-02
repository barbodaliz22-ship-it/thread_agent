"""
Market data models. Phase 2 ships OHLCV only — order book, derivatives,
on-chain, news, and sentiment tables follow the same pattern in later
phases (each gets a `source`, business `timestamp`, `asset`, ingestion
timestamp, and `quality_status`, per the Master Prompt's data-quality
rules in section 6).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin
from app.models.enums import DataQualityStatus, Timeframe


class OHLCVBar(TimestampMixin, Base):
    """
    A single OHLCV candle for one asset/timeframe/source at one point in
    time. `timestamp` is the *business* time (the candle's open time),
    distinct from TimestampMixin's `ingested_at` (when our system saw it).
    """

    __tablename__ = "ohlcv_bars"
    __table_args__ = (
        # A given source should never report two different bars for the
        # same asset/timeframe/timestamp — this is the DB-level guard
        # against the "duplicate records" failure mode from section 6.
        UniqueConstraint(
            "source", "asset", "timeframe", "timestamp", name="uq_ohlcv_source_asset_tf_ts"
        ),
        Index("ix_ohlcv_asset_timeframe_timestamp", "asset", "timeframe", "timestamp"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    source: Mapped[str] = mapped_column(String(64), nullable=False)
    asset: Mapped[str] = mapped_column(String(32), nullable=False)  # e.g. "BTC-USD"
    timeframe: Mapped[Timeframe] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)

    open: Mapped[float] = mapped_column(Numeric(24, 8), nullable=False)
    high: Mapped[float] = mapped_column(Numeric(24, 8), nullable=False)
    low: Mapped[float] = mapped_column(Numeric(24, 8), nullable=False)
    close: Mapped[float] = mapped_column(Numeric(24, 8), nullable=False)
    volume: Mapped[float] = mapped_column(Numeric(32, 8), nullable=False)

    quality_status: Mapped[DataQualityStatus] = mapped_column(
        default=DataQualityStatus.OK, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<OHLCVBar {self.source}:{self.asset}:{self.timeframe.value} "
            f"@ {self.timestamp.isoformat()}>"
        )
