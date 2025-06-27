from shiny import reactive
import plotly.graph_objects as go
from data_loader import load_metrics
from shinywidgets import output_widget, render_widget  

metrics_dict = load_metrics()

def server(input, output, session):
    @render_widget
    @reactive.event(input.select, input.checkbox_group, input.slider, input.slider2)
    def basic_plot():
        df = metrics_dict.get(input.select(), None)
        if df is None:
            return go.Figure()

        fig = go.Figure()

        for metric in input.checkbox_group():
            if metric in df.columns:
                fig.add_trace(go.Scatter(
                    x=df["Threshold"],
                    y=df[metric],
                    mode='lines',
                    name=metric
                ))

        fig.update_layout(
            title='Confusion Matrix Components vs. Thresholds',
            xaxis=dict(title="Threshold", showgrid=True, range=input.slider()),
            yaxis=dict(title='Metrics', showgrid=True),
            template='simple_white',
            legend=dict(title='Metrics'),
            width=800,
            height=500
        )

        return fig
    
    @render_widget
    @reactive.event(input.select_metric, input.checkbox_group_version_gr, input.slider_xaxis_compare, input.slider_yaxis_compare)
    def compare_plot():
        metric = input.select_metric()
        fig = go.Figure()

        for version in input.checkbox_group_version_gr():
            df = metrics_dict.get(version, None)
            if df is None:
                continue

            fig.add_trace(go.Scatter(
                    x=df["Threshold"],
                    y=df[metric],
                    mode='lines',
                    name=version
                ))
         
        fig.update_layout(
            title='Confusion Matrix Components vs. Thresholds',
            xaxis=dict(title="Threshold", showgrid=True, range=input.slider_xaxis_compare()),
            yaxis=dict(title='Metrics', showgrid=True),
            template='simple_white',
            legend=dict(title='Metrics'),
            width=800,
            height=500
        )

        return fig