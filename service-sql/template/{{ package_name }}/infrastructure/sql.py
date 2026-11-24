"""SQLAlchemy 2 storage for examples. SQLite by default; any SQLAlchemy URL works."""

from sqlalchemy import Integer, String, create_engine, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from ..domain.examples import Example


class Base(DeclarativeBase):
    """Declarative base for the tables this service owns."""


class ExampleRow(Base):
    """The `examples` table."""

    __tablename__ = "examples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))


def _to_domain(row: ExampleRow) -> Example:
    return Example(id=row.id, name=row.name, description=row.description)


class SqlExampleRepository:
    """Stores examples in the `examples` table. Each method runs in its own transaction."""

    def __init__(self, url: str) -> None:
        self.engine: Engine = create_engine(url, pool_pre_ping=True)
        self._sessions = sessionmaker(bind=self.engine, expire_on_commit=False)

    def create_tables(self) -> None:
        """Create missing tables. There are no migrations, so schema changes need a plan."""
        Base.metadata.create_all(self.engine)

    def ping(self) -> None:
        """Readiness check: run a trivial query."""
        with self.engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    def dispose(self) -> None:
        """Close every pooled connection."""
        self.engine.dispose()

    def add(self, name: str, description: str) -> Example:
        """Store a new example and return it with its identifier."""
        with self._sessions.begin() as session:
            row = ExampleRow(name=name, description=description)
            session.add(row)
            session.flush()
            return _to_domain(row)

    def get(self, example_id: int) -> Example | None:
        """Return one example, or None."""
        with self._sessions() as session:
            row = session.get(ExampleRow, example_id)
            return _to_domain(row) if row is not None else None

    def page(self, *, offset: int, limit: int) -> list[Example]:
        """Return examples in creation order."""
        statement = select(ExampleRow).order_by(ExampleRow.id).offset(offset).limit(limit)
        with self._sessions() as session:
            return [_to_domain(row) for row in session.scalars(statement)]

    def delete(self, example_id: int) -> bool:
        """Remove one example; return False when it did not exist."""
        with self._sessions.begin() as session:
            row = session.get(ExampleRow, example_id)
            if row is None:
                return False
            session.delete(row)
            return True
