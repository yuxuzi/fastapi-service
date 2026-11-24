"""Request and response bodies, kept apart from the domain model."""

from pydantic import BaseModel, ConfigDict, Field


class ExampleCreate(BaseModel):
    """Request body for creating an example."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)


class ExampleRead(BaseModel):
    """Response body for one example."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
