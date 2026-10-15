"""Small JSON logging configuration based on the standard library."""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime

EXTRA_FIELDS = (
    "event",
    "service",
    "request_id",
    "method",
    "route",
    "status_code",
    "duration_ms",
    "error_type",
)


class JsonFormatter(logging.Formatter):
    """Render one structured JSON object per log record."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "event": getattr(record, "event", record.getMessage()),
            "service": getattr(record, "service", "unknown"),
        }
        for field in EXTRA_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def configure_logging(level: str) -> None:
    """Install a deterministic root handler and silence duplicate access logs."""

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)

    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
