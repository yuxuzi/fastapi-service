"""The application factory: settings and repository in, a configured FastAPI app out."""

import logging
import re
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .api import errors, examples, health
from .domain.ports import ExampleRepository
from .infrastructure.memory import InMemoryExampleRepository
from .logs import configure_logging, request_id
from .settings import Settings, get_settings

logger = logging.getLogger(__name__)
REQUEST_ID_HEADER = "X-Request-ID"
_INCOMING_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


def create_app(
    settings: Settings | None = None,
    repository: ExampleRepository | None = None,
) -> FastAPI:
    """Build the application. Pass `repository` to replace the storage, for example in tests."""
    config = settings or get_settings()
    configure_logging(config.LOG_LEVEL, config.LOG_FORMAT)
    if repository is None:
        repository = InMemoryExampleRepository()

    app = FastAPI(
        title=config.APP_NAME,
        version=config.APP_VERSION,
        debug=config.DEBUG,
    )
    app.state.settings = config
    app.state.repository = repository
    app.state.readiness_checks = {}

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=config.ALLOWED_HOSTS)
    errors.register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(examples.router)

    @app.middleware("http")
    async def request_context(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Give each request an ID, echo it back, and log one line per request."""
        incoming = request.headers.get(REQUEST_ID_HEADER, "")
        current = incoming if _INCOMING_ID.fullmatch(incoming) else uuid.uuid4().hex
        token = request_id.set(current)
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers[REQUEST_ID_HEADER] = current
            return response
        finally:
            logger.info(
                "%s %s -> %s",
                request.method,
                request.url.path,
                status_code,
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": status_code,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                },
            )
            request_id.reset(token)

    return app
