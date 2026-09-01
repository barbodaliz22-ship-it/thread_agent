import pytest

from app.config.settings import Environment, Settings, TradingMode, get_settings


def test_default_trading_mode_is_research_only():
    """The default must always be the safest mode, even with no .env present."""
    settings = Settings(_env_file=None)
    assert settings.trading_mode == TradingMode.RESEARCH_ONLY
    assert settings.live_trading_enabled is False


def test_live_trading_flag_only_true_when_explicitly_set():
    settings = Settings(_env_file=None, trading_mode=TradingMode.LIVE)
    assert settings.live_trading_enabled is True


def test_get_settings_is_cached():
    a = get_settings()
    b = get_settings()
    assert a is b


def test_environment_enum_values():
    assert Environment.LOCAL.value == "local"
    assert Environment.PRODUCTION.value == "production"
