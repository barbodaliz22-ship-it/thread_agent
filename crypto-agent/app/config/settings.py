"""
Central application configuration.

All configuration is loaded from environment variables (see .env.example).
No secrets are ever hard-coded here.
"""
from __future__ import annotations

from enum import Enum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class TradingMode(str, Enum):
    """
    Controls what the execution layer is allowed to do.

    RESEARCH_ONLY: no orders of any kind, data collection / backtesting only.
    PAPER: simulated orders against a virtual portfolio, no real funds.
    LIVE: real orders through an exchange API.

    The system must default to the safest mode. LIVE must never be reachable
    without an explicit, deliberate operator action outside of this codebase
    (e.g. setting TRADING_MODE=live AND passing a live-safety checklist).
    """

    RESEARCH_ONLY = "research_only"
    PAPER = "paper"
    LIVE = "live"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App metadata ---
    app_name: str = "crypto-research-agent"
    app_version: str = "0.1.0"
    environment: Environment = Environment.LOCAL
    debug: bool = False

    # --- Safety / trading mode ---
    # Hard default is the safest possible mode. This must be changed
    # explicitly and deliberately, never implicitly.
    trading_mode: TradingMode = TradingMode.RESEARCH_ONLY

    # --- API server ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # --- Database ---
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/crypto_agent",
        description="SQLAlchemy async connection string for PostgreSQL.",
    )

    # --- Cache / queue ---
    redis_url: str = Field(default="redis://localhost:6379/0")

    # --- Logging ---
    log_level: str = "INFO"
    log_json: bool = True

    # --- External API keys (all optional at this phase; nothing is called yet) ---
    exchange_api_key: str | None = None
    exchange_api_secret: str | None = None
    news_api_key: str | None = None
    onchain_api_key: str | None = None
    sentiment_api_key: str | None = None

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    @property
    def live_trading_enabled(self) -> bool:
        """
        Single source of truth for whether the system is allowed to place
        real orders. Every execution-layer entry point must check this
        (and additional safety gates) before ever touching a live API.
        """
        return self.trading_mode == TradingMode.LIVE


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor — import and call this, don't instantiate Settings() directly."""
    return Settings()
