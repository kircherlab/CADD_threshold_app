import plotly.graph_objects as go
import pandas as pd


def make_basic_plot(
    df: pd.DataFrame,
    selected_metrics: list,
    slider_range: list,
    title_label: str,
    y_axis_label: str,
    x_axis_label: str,
    legend_label: str,
) -> go.Figure:
    """This function creates a basic line plot showing selected metrics for one dataset"""
    fig = go.Figure()

    if df is None:
        return fig

    for metric in selected_metrics:
        if metric in df.columns:
            fig.add_trace(
                go.Scatter(x=df["Threshold"], y=df[metric], mode="lines", name=metric)
            )

    fig.update_layout(
        title=title_label,
        xaxis=dict(title=x_axis_label, showgrid=True, range=slider_range),
        yaxis=dict(title=y_axis_label, showgrid=True),
        template="simple_white",
        legend=dict(title=legend_label),
        height=600,
        autosize=True,
    )

    return fig
