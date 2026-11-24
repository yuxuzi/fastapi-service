"""Example use cases."""

from ..domain.examples import Example, ExampleNotFoundError
from ..domain.ports import ExampleRepository


class ExampleService:
    """Create, read, page, and delete examples through the repository port."""

    def __init__(self, repository: ExampleRepository) -> None:
        self._repository = repository

    def create(self, name: str, description: str) -> Example:
        """Store a new example."""
        return self._repository.add(name, description)

    def get(self, example_id: int) -> Example:
        """Return one example or raise `ExampleNotFoundError`."""
        example = self._repository.get(example_id)
        if example is None:
            raise ExampleNotFoundError(f"Example {example_id} was not found.")
        return example

    def page(self, *, offset: int, limit: int) -> list[Example]:
        """Return one page of examples."""
        return self._repository.page(offset=offset, limit=limit)

    def delete(self, example_id: int) -> None:
        """Delete one example or raise `ExampleNotFoundError`."""
        if not self._repository.delete(example_id):
            raise ExampleNotFoundError(f"Example {example_id} was not found.")
