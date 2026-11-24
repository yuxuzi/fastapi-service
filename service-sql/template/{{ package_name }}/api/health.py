"""Liveness (`/health`) and readiness (`/ready`) for orchestrators and load balancers."""

import logging
from typing import Literal

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])
_UNAVAILABLE = 503


class Liveness(BaseModel):
    """The process is up."""

    status: Literal["ok"] = "ok"
    version: str


class Readiness(BaseModel):
    """Whether every readiness check passes."""

    status: Literal["ok", "unavailable"]
    checks: dict[str, Literal["ok", "failed"]]


@router.get("/health")
def health(request: Request) -> Liveness:
    """Report that the process is running. Never touches dependencies."""
    return Liveness(version=request.app.state.settings.APP_VERSION)


@router.get("/ready", responses={_UNAVAILABLE: {"model": Readiness}})
def ready(request: Request, response: Response) -> Readiness:
    """Run every readiness check; one failure makes the service unavailable."""
    checks: dict[str, Literal["ok", "failed"]] = {}
    for name, check in request.app.state.readiness_checks.items():
        try:
            check()
        except Exception:
            logger.warning("Readiness check %s failed", name, exc_info=True)
            checks[name] = "failed"
        else:
            checks[name] = "ok"
    healthy = all(result == "ok" for result in checks.values())
    if not healthy:
        response.status_code = _UNAVAILABLE
    return Readiness(status="ok" if healthy else "unavailable", checks=checks)
