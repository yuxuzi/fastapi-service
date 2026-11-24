"""FastAPI dependencies: handlers get their services here, never by building adapters."""

from typing import Annotated

from fastapi import Depends, Request

from ..application.examples import ExampleService
from ..domain.ports import ExampleRepository


def get_example_service(request: Request) -> ExampleService:
    """Build the example service over the repository the application was created with."""
    repository: ExampleRepository = request.app.state.repository
    return ExampleService(repository)


ExampleServiceDep = Annotated[ExampleService, Depends(get_example_service)]
