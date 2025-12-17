import plotly.graph_objects as go
import pandas as pd
from modules.functions_server_helpers import categorize_label


def make_basic_bar_plot(
    df: pd.DataFrame,
    steps: int,
    type: str,
    title_text: str,
    xaxis_text: str,
    yaxis_text: str,
    legend_text: str,
    range_xaxis: list,
) -> pd.DataFrame:
    """This function creates a stacked bar plot showing the distribution of ClinVar variants
    across PHRED score thresholds or genes in steps of given size.
    Type can be "standard" for PHRED score bins or "gene" for gene-wise distribution.
    """
    if df is None or df.empty:
        return go.Figure()

    data = df.copy()
    data["category"] = data["ClinicalSignificance"].apply(categorize_label)

    if type == "standard":

        bins = range(0, 100 + steps, steps)
        labels = [f"{i}-{i + steps}" for i in range(0, 100, steps)]
        data["score_bin"] = pd.cut(
            data["PHRED"], bins=bins, labels=labels, include_lowest=True, right=False
        )

        grouped = (
            data.groupby(["score_bin", "category"], observed=True)
            .size()
            .unstack(fill_value=0)
        )
        grouped = grouped.reindex(labels, fill_value=0)

    if type == "gene":
        data["category"] = data["ClinicalSignificance"].apply(categorize_label)
        grouped = (
            data.groupby([data["GeneName"], "category"], observed=True)
            .size()
            .unstack(fill_value=0)
        )
        grouped = grouped.loc[grouped.sum(axis=1).sort_values(ascending=False).index]

    fig = go.Figure()
    colors = {
        "pathogenic": "#7b3294",
        "likely pathogenic": "#c2a5cf",
        "benign": "#008837",
        "likely benign": "#a6dba0",
        "unknown": "#f7f7f7",
    }

    for category in grouped.columns:
        fig.add_trace(
            go.Bar(
                x=grouped.index.astype(str),
                y=grouped[category],
                name=category,
                marker_color=colors.get(category, "#333333"),
                text=grouped[category],
                textposition="inside",
            )
        )

    # Add "total count of variants"-annotations on top of each bar
    totals = grouped.sum(axis=1)
    for i, total in enumerate(totals):
        fig.add_annotation(
            x=grouped.index[i],
            y=total,
            text=str(total),
            showarrow=False,
            yshift=10,
            font=dict(size=10, color="black", family="Arial Black"),
        )

    fig.update_layout(
        barmode="stack",
        title=title_text,
        xaxis_title=xaxis_text,
        yaxis_title=yaxis_text,
        legend_title=legend_text,
        height=800,
        autosize=True,
        xaxis=dict(type="category", range=range_xaxis),
        xaxis_tickangle=-45,
    )

    return fig
