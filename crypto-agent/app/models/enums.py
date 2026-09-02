"""
Shared enums used across ORM models. Kept in one place so the DB layer
and the Pydantic schemas can both import the same source of truth.
"""
from __future__ import annotations

import enum


class DataQualityStatus(str, enum.Enum):
    """
    Per the Master Prompt's data-quality rules (section 6): every ingested
    row must carry a quality status, and the trading engine must never
    act on data flagged anything other than OK.
    """

    OK = "ok"
    STALE = "stale"
    MISSING_FIELDS = "missing_fields"
    DUPLICATE = "duplicate"
    IMPOSSIBLE_VALUE = "impossible_value"
    SOURCE_ERROR = "source_error"


class Timeframe(str, enum.Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
