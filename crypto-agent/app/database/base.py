"""
Declarative base and shared mixins for all ORM models.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    """
    Every table that stores ingested or generated data gets these two
    columns. This is required by the Master Prompt's data-quality rules:
    every dataset must carry both when the underlying event happened
    (business timestamp, defined per-model) and when *we* ingested it.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
