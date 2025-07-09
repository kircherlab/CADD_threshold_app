from .data_processing import register_data_processing
from .metrics import register_metrics
from .plots import register_plots
from data_loader import load_metrics, load_metrics_bar

metrics_dict = load_metrics()
metrics_dict_bar = load_metrics_bar()


def server(input, output, session):
    register_data_processing(input, output, session)
    register_plots(input, output, session)
    register_metrics(input, output, session)
    