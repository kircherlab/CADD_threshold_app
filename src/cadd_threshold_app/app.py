from pathlib import Path

import starlette.routing
from shiny import App

from .server_logic import server
from .ui_components import get_ui

APP_ROOT = Path(__file__).resolve().parent

app = App(get_ui(), server, static_assets={"/www": APP_ROOT / "www"})

# Some proxies request /websocket (without trailing slash), while Shiny registers
# /websocket/. Add an alias so both forms are accepted.
if hasattr(app, "_on_connect_cb"):
    app.starlette_app.router.routes.insert(
        0,
        starlette.routing.WebSocketRoute("/websocket", app._on_connect_cb),
    )
