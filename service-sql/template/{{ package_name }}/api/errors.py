"""Map domain errors to HTTP responses."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ..domain.examples import ExampleNotFoundError


async def _not_found(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


def register_error_handlers(app: FastAPI) -> None:
    """Install the handlers for domain errors."""
    app.add_exception_handler(ExampleNotFoundError, _not_found)
