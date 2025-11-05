import plotly.graph_objects as go


def make_basic_plot(df, selected_metrics, slider_range):
    fig = go.Figure()

    if df is None:
        return fig

    for metric in selected_metrics:
        if metric in df.columns:
            fig.add_trace(
                go.Scatter(x=df["Threshold"], y=df[metric], mode="lines", name=metric)
            )

    fig.update_layout(
        title="Metrics at different thresholds",
        xaxis=dict(title="Threshold", showgrid=True, range=slider_range),
        yaxis=dict(title="Metrics (Number of variants or percent)", showgrid=True),
        template="simple_white",
        legend=dict(title="Metrics"),
        width=800,
        height=500,
    )

    return fig
