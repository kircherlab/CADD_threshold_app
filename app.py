from shiny import App
from ui_components import get_ui
from server_logic import server

app = App(get_ui(), server)