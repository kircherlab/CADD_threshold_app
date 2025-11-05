import plotly.graph_objects as go
import pandas as pd
from modules.functions import categorize_label


def make_basic_bar_plot(df, steps):
    if df is None:
        return go.Figure()

    # 1. standardize the clinical significance labels into 4 categories (benign, likely benign, pathogenic, likely pathogenic)
    # 2. make bins from 0 to 100 in steps of 10
    # 3. map each variant to its corresponding bin based on its PHRED score
    # 4. count the number of variants in each bin for each category (table with index as bins and columns as categories)

    data = df.copy()
    data["category"] = data["ClinicalSignificance"].apply(categorize_label)

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

    # make a figure
    # define the colors for each category
    # create a stacked bar plot from the table
    # add total count annotations on top of each bar

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
        title="Distribution of ClinVar variants from threshold 0 to 100 in steps of 10",
        xaxis_title="PHRED Score",
        yaxis_title="Number of variants",
        legend_title="Clinical Classification from ClinVar",
        height=800,
        width=2000,
        xaxis=dict(type="category"),
    )

    return fig
