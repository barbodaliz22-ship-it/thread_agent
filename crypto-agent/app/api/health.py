"""
Health and readiness endpoints.

/health   -> liveness: is the process up at all.
/readiness -> readiness: are dependencies (db, cache, etc.) reachable.
              At this phase there are no real dependencies wired in yet,
              so readiness checks are stubbed but structured for future use.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.config.settings import get_settings
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        app_version=settings.app_version,
        environment=settings.environment.value,
        trading_mode=settings.trading_mode.value,
    )


@router.get("/readiness", response_model=ReadinessResponse)
async def readiness() -> ReadinessResponse:
    # Phase 1: no external dependencies are wired up yet (no DB session,
    # no Redis client). This endpoint exists now so later phases can add
    # real checks (db.ping(), redis.ping(), ...) without changing the
    # contract that callers/monitoring already depend on.
    checks = {
        "database": "not_configured",
        "cache": "not_configured",
    }
    overall = "ok" if all(v in ("ok", "not_configured") for v in checks.values()) else "degraded"
    return ReadinessResponse(status=overall, checks=checks)
