import pandas as pd
import plotly.graph_objects as go


def make_basic_plot(
    df: pd.DataFrame,
    selected_metrics: list,
    slider_range: list,
    metric_type: str = None,
    title_label: str = "",
    y_axis_label: str = "",
    x_axis_label: str = "",
    legend_label: str = "",
) -> go.Figure:
    """This function creates a basic line plot showing selected metrics for one dataset"""
    fig = go.Figure()

    if df is None:
        return fig

    # Prepare presence check for confusion-matrix count columns
    count_cols = ["TrueNegatives", "FalsePositives", "FalseNegatives", "TruePositives"]
    has_counts = all(c in df.columns for c in count_cols)

    for metric in selected_metrics:
        if metric not in df.columns:
            continue

        # For confusion-matrix count metrics, plot raw counts on a secondary y-axis
        # so totals are visible while other metrics remain on the primary axis.
        if metric in count_cols and has_counts:
            # show axis membership in the legend name for clarity
            fig.add_trace(
                go.Scatter(
                    x=df["Threshold"],
                    y=df[metric],
                    mode="lines",
                    name=f"{metric} (right axis)",
                    yaxis="y2",
                )
            )
        else:
            # Non-count metrics plotted on primary y-axis
            fig.add_trace(go.Scatter(x=df["Threshold"], y=df[metric], mode="lines", name=f"{metric} (primary axis)"))

    fig.update_layout(
        title=title_label,
        xaxis=dict(title=x_axis_label, showgrid=True, range=slider_range),
        yaxis=dict(title=y_axis_label, showgrid=True),
        yaxis2=dict(
            title="Total variants",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        template="simple_white",
        legend=dict(title=legend_label),
        height=600,
        autosize=True,
    )

    return fig
