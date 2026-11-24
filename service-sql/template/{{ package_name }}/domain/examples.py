"""The example entity and the error raised when one is missing."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Example:
    """A stored example."""

    id: int
    name: str
    description: str


class ExampleNotFoundError(LookupError):
    """No example has the requested identifier."""
