"""In-memory storage: the default for development and tests. Data is lost on restart."""

import threading

from ..domain.examples import Example


class InMemoryExampleRepository:
    """Examples in a dict guarded by a lock, because requests run on a thread pool."""

    def __init__(self) -> None:
        self._rows: dict[int, Example] = {}
        self._next_id = 1
        self._lock = threading.Lock()

    def add(self, name: str, description: str) -> Example:
        """Store a new example."""
        with self._lock:
            example = Example(id=self._next_id, name=name, description=description)
            self._rows[example.id] = example
            self._next_id += 1
            return example

    def get(self, example_id: int) -> Example | None:
        """Return one example, or None."""
        with self._lock:
            return self._rows.get(example_id)

    def page(self, *, offset: int, limit: int) -> list[Example]:
        """Return examples in creation order."""
        with self._lock:
            return list(self._rows.values())[offset : offset + limit]

    def delete(self, example_id: int) -> bool:
        """Remove one example."""
        with self._lock:
            return self._rows.pop(example_id, None) is not None
