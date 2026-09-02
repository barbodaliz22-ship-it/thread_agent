"""
Health and readiness endpoints.

/health   -> liveness: is the process up at all.
/readiness -> readiness: are dependencies (db, cache, etc.) reachable.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.config.settings import get_settings
from app.database.session import ping_database
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
    db_ok = await ping_database()

    checks = {
        "database": "ok" if db_ok else "unreachable",
        # Redis isn't used by anything yet (no cache/queue consumer exists),
        # so it's intentionally left unchecked rather than reported as a
        # false "ok" — this becomes a real check once something depends on it.
        "cache": "not_configured",
    }
    overall = "ok" if checks["database"] == "ok" else "degraded"
    return ReadinessResponse(status=overall, checks=checks)
