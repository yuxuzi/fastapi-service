"""ASGI entry point: `uvicorn <package>.main:app`."""

from .app import create_app

app = create_app()
