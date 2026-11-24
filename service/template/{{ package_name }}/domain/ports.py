"""Ports: what the application needs from storage. Infrastructure implements them."""

from typing import Protocol

from .examples import Example


class ExampleRepository(Protocol):
    """Stores and finds examples."""

    def add(self, name: str, description: str) -> Example:
        """Store a new example and return it with its identifier."""
        ...

    def get(self, example_id: int) -> Example | None:
        """Return one example, or None when it does not exist."""
        ...

    def page(self, *, offset: int, limit: int) -> list[Example]:
        """Return examples in creation order."""
        ...

    def delete(self, example_id: int) -> bool:
        """Remove one example; return False when it did not exist."""
        ...
