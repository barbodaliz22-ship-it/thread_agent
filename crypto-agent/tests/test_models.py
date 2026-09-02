from app.database.base import Base
from app.models.enums import DataQualityStatus, Timeframe
from app.models.market_data import OHLCVBar


def test_ohlcv_bar_table_name():
    assert OHLCVBar.__tablename__ == "ohlcv_bars"


def test_ohlcv_bar_is_registered_on_base_metadata():
    assert "ohlcv_bars" in Base.metadata.tables


def test_ohlcv_bar_has_expected_columns():
    columns = {c.name for c in OHLCVBar.__table__.columns}
    expected = {
        "id",
        "created_at",
        "ingested_at",
        "source",
        "asset",
        "timeframe",
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quality_status",
    }
    assert expected.issubset(columns)


def test_ohlcv_bar_has_unique_constraint_on_natural_key():
    constraint_columns = {
        tuple(c.name for c in uc.columns) for uc in OHLCVBar.__table__.constraints
        if hasattr(uc, "columns") and len(uc.columns) > 1
    }
    assert ("source", "asset", "timeframe", "timestamp") in constraint_columns


def test_data_quality_status_values():
    assert DataQualityStatus.OK.value == "ok"
    assert DataQualityStatus.DUPLICATE.value == "duplicate"


def test_timeframe_values():
    assert Timeframe.H1.value == "1h"
    assert Timeframe.D1.value == "1d"
