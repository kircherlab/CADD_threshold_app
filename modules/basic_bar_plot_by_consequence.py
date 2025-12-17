import pandas as pd
from modules.functions_server_helpers import categorize_label
import plotly.express as px
import plotly.graph_objects as go
from plotly.colors import sample_colorscale


def make_basic_bar_plot_by_consequence(data: pd.DataFrame) -> pd.DataFrame:
    if data is None:
        return go.Figure()

    # data = df.copy()
    ''' this function creates a stacked bar plot showing the distribution of variant consequences
    across PHRED score thresholds for pathogenic and likely pathogenic variants.
    '''

    data["category"] = data["ClinicalSignificance"].apply(categorize_label)
    data_filtered = data[
        data["category"].isin(["pathogenic", "likely pathogenic"])
    ].copy()

    bins = list(range(0, 101))
    labels = [f"{i}-{i + 1}" for i in range(0, 100)]
    data_filtered["score_bin"] = pd.cut(
        data_filtered["PHRED"],
        bins=bins,
        labels=labels,
        include_lowest=True,
        right=False,
    )

    # count the number of variants in each bin for each consequence and category (table with index as bins and columns as consequences)
    grouped = (
        data_filtered.groupby(["score_bin", "category", "Consequence"], observed=False)
        .size()
        .reset_index(name="count")
    )

    # for each consequence, create a stacked bar plot for pathogenic and likely pathogenic categories
    fig = go.Figure()
    categories = ["pathogenic", "likely pathogenic"]
    consequences = grouped["Consequence"].unique()

    n = max(len(consequences), 10)
    expanded_palette = sample_colorscale(
        px.colors.diverging.Portland, [i / (n - 1) for i in range(n)]
    )
    color_map = {cons: expanded_palette[i] for i, cons in enumerate(consequences)}

    for cons in consequences:
        for cat in categories:
            df_cons = grouped[
                (grouped["Consequence"] == cons) & (grouped["category"] == cat)
            ]
            if not df_cons.empty:
                fig.add_trace(
                    go.Bar(
                        x=df_cons["score_bin"],
                        y=df_cons["count"],
                        name=cons,
                        offsetgroup=cat,
                        legendgroup=cons,
                        showlegend=(cat == "pathogenic"),
                        marker_color=color_map[cons],
                        opacity=0.6 if cat == "likely pathogenic" else 1.0,
                        hovertemplate=f"%{{x}}<br>{cat}<br>{cons}: %{{y}}<extra></extra>",
                    )
                )

    fig.update_layout(
        barmode="stack",
        xaxis=dict(type="category"),
        title="Distribution of variant consequences across thresholds for pathogenic/likely pathogenic variants",
        xaxis_title="PHRED Score",
        yaxis_title="Number of variants",
        height=800,
        autosize=True,
    )
    return fig
