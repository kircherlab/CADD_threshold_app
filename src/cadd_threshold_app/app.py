from pathlib import Path

from shiny import App

from .server_logic import server
from .ui_components import get_ui

APP_ROOT = Path(__file__).resolve().parent

app = App(get_ui(), server, static_assets={"/www": APP_ROOT / "www"})
