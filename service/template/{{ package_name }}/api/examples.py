"""Example endpoints: each handler translates HTTP to a service call and back."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from .deps import ExampleServiceDep
from .schemas import ExampleCreate, ExampleRead

router = APIRouter(prefix="/api/v1/examples", tags=["examples"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_example(payload: ExampleCreate, service: ExampleServiceDep) -> ExampleRead:
    """Create an example."""
    return ExampleRead.model_validate(service.create(payload.name, payload.description))


@router.get("")
def list_examples(
    service: ExampleServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ExampleRead]:
    """List examples in creation order."""
    return [ExampleRead.model_validate(item) for item in service.page(offset=offset, limit=limit)]


@router.get("/{example_id}")
def get_example(example_id: int, service: ExampleServiceDep) -> ExampleRead:
    """Return one example, or 404."""
    return ExampleRead.model_validate(service.get(example_id))


@router.delete("/{example_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_example(example_id: int, service: ExampleServiceDep) -> None:
    """Delete one example, or 404."""
    service.delete(example_id)
