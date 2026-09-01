"""
Structured logging configuration.

Uses stdlib logging with a JSON formatter so logs are machine-parseable
in production, and a human-friendly formatter for local development.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from app.config.settings import get_settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        # allow callers to pass structured extras: logger.info("msg", extra={"extra_fields": {...}})
        extra_fields = getattr(record, "extra_fields", None)
        if extra_fields:
            payload.update(extra_fields)

        return json.dumps(payload, default=str)


def configure_logging() -> None:
    settings = get_settings()

    root = logging.getLogger()
    root.setLevel(settings.log_level.upper())

    # Clear any pre-existing handlers (avoids duplicate logs on reload).
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if settings.log_json:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root.addHandler(handler)

    # Quiet down noisy third-party loggers by default.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
