from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import app

__all__ = ["app"]


def __getattr__(name):
    if name == "app":
        # Import lazily so CLI startup can set env vars before app construction.
        return import_module(".app", __name__).app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
