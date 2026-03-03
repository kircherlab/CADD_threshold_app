from shiny import App

from .server_logic import server
from .ui_components import get_ui

app = App(get_ui(), server)
