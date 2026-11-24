"""Structured logs: one JSON object per line, with the request ID on every record."""

import json
import logging
from contextvars import ContextVar
from datetime import UTC, datetime

request_id: ContextVar[str | None] = ContextVar("request_id", default=None)

_EXTRA_FIELDS = ("method", "path", "status", "duration_ms")
_HANDLER_NAME = "service-logs"
_TEXT_FORMAT = "%(asctime)s %(levelname)s %(name)s [%(request_id)s] %(message)s"


class RequestIdFilter(logging.Filter):
    """Attach the current request ID to every record that passes through the handler."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Annotate the record; never drops it."""
        record.__dict__["request_id"] = request_id.get()
        return True


class JsonFormatter(logging.Formatter):
    """Render one record as one JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        """Serialize the message, request ID, and any request fields."""
        payload: dict[str, object] = {
            "time": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": record.__dict__.get("request_id"),
        }
        for key in _EXTRA_FIELDS:
            if key in record.__dict__:
                payload[key] = record.__dict__[key]
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str, log_format: str) -> None:
    """Install one handler on the root logger, replacing the one an earlier call installed."""
    handler = logging.StreamHandler()
    handler.name = _HANDLER_NAME
    handler.addFilter(RequestIdFilter())
    if log_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(_TEXT_FORMAT))
    root = logging.getLogger()
    for existing in [h for h in root.handlers if h.name == _HANDLER_NAME]:
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(level)
