from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app_name: str
    app_version: str
    environment: str
    trading_mode: str


class ReadinessResponse(BaseModel):
    status: str
    checks: dict[str, str]
