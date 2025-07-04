from shiny import reactive, render_text, render
import plotly.graph_objects as go
from data_loader import load_metrics, load_metrics_bar
from shinywidgets import output_widget, render_widget 
import pandas as pd 
from pathlib import Path
import numpy as np
metrics_dict = load_metrics()
metrics_dict_bar = load_metrics_bar()
