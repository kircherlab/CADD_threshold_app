import plotly.graph_objects as go
from data_loader import load_metrics


def make_compare_basic_plot(metric: str, selected_versions, xaxis_range) -> go.Figure:
    ''' This function creates a comparison line plot for different given datasets showing the given metric'''
    fig = go.Figure()

    for version in selected_versions:
        df = load_metrics(version)
        if df is None:
            continue

        fig.add_trace(
            go.Scatter(x=df["Threshold"], y=df[metric], mode="lines", name=version)
        )

    fig.update_layout(
        title="Confusion Matrix Components vs. Thresholds",
        xaxis=dict(
            title="Threshold", showgrid=True, range=xaxis_range
        ),
        yaxis=dict(title="Metrics", showgrid=True),
        template="simple_white",
        legend=dict(title="Metrics"),
        width=800,
        height=500,
    )
    return fig
