"""
Verifies the hard safety gate in app.main.lifespan: the app must refuse
to start if TRADING_MODE=live, since no execution/risk layer exists yet.
"""
import pytest
from fastapi.testclient import TestClient

from app.config.settings import Settings, TradingMode, get_settings
import app.main as main_module


def test_app_refuses_to_start_in_live_mode(monkeypatch):
    live_settings = Settings(_env_file=None, trading_mode=TradingMode.LIVE)

    monkeypatch.setattr(main_module, "get_settings", lambda: live_settings)
    get_settings.cache_clear()

    app = main_module.create_app()

    with pytest.raises(RuntimeError, match="Refusing to start"):
        with TestClient(app):
            pass

    get_settings.cache_clear()
