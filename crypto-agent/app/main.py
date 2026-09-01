"""
Application entrypoint.

Phase 1 scope: app skeleton, config, structured logging, and health
endpoints only. No data collection, no strategies, no execution — those
are built in later phases on top of this foundation.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.config.logging_config import configure_logging
from app.config.settings import get_settings

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(
        "Starting application",
        extra={
            "extra_fields": {
                "app_name": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment.value,
                "trading_mode": settings.trading_mode.value,
            }
        },
    )

    if settings.live_trading_enabled:
        # Hard stop: live trading is not implemented yet in any phase so far.
        # This guard exists from day one so it is never possible to silently
        # ship a config that enables live orders before the execution layer,
        # risk layer, and safety checklist actually exist.
        raise RuntimeError(
            "TRADING_MODE=live is set, but live trading is not implemented yet. "
            "Refusing to start. Use 'research_only' or 'paper' instead."
        )

    yield

    logger.info("Shutting down application")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.include_router(health_router)

    return app


app = create_app()
