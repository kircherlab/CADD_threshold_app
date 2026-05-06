import pandas as pd
import plotly.graph_objects as go


def make_basic_plot(
    df: pd.DataFrame,
    selected_metrics: list,
    slider_range: list,
    metric_type: str,
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
            # If requested, display counts as decimal percentages for confusion-matrix counts
            if (
                metric_type == "percentage"
                and metric in [
                    "FalsePositives",
                    "FalseNegatives",
                    "TruePositives",
                    "TrueNegatives",
                ]
            ):
                cols = ["TrueNegatives", "FalsePositives", "FalseNegatives", "TruePositives"]
                # Compute total per row; avoid division by zero by setting result to 0 when total==0
                if all(c in df.columns for c in cols):
                    totals = df[cols].sum(axis=1)
                    y = df[metric] / totals.where(totals > 0)
                    y = y.fillna(0.0)
                else:
                    y = df[metric]
            else:
                y = df[metric]

            fig.add_trace(go.Scatter(x=df["Threshold"], y=y, mode="lines", name=metric))

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
