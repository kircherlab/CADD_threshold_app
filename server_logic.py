from shiny import reactive, render, ui
import starlette.responses
import plotly.graph_objects as go
from shinywidgets import render_widget
import pandas as pd
from io import StringIO

from data_loader import load_metrics, load_metrics_bar
from modules.basic_plot import make_basic_plot
from modules.basic_bar_plot import make_basic_bar_plot
from modules.basic_bar_plot_consequence_pathogenic import (
    make_basic_bar_plot_consequence_pathogenic,
)
from modules.functions import (
    categorize_label,
    genes_from_list_or_file,
    has_matching_gene,
    calculate_metrics,
)


def server(input, output, session):

    @output
    @render.ui
    def out():
        # Register a dynamic route for the client to try to connect to.
        # It does nothing, just the 200 status code is all that the client
        # will care about.
        url = session.dynamic_route(
            "test",
            lambda req: starlette.responses.PlainTextResponse(
                "OK", headers={"Cache-Control": "no-cache"}
            ),
        )

        # Send JS code to the client to repeatedly hit the dynamic route.
        # It will succeed if and only if we reach the correct Python
        # process.
        return ui.tags.script(
            f"""
            const url = "{url}";
            const count_el = document.getElementById("count");
            const status_el = document.getElementById("status");
            let count = 0;
            async function check_url() {{
                count_el.innerHTML = ++count;
                try {{
                    const resp = await fetch(url);
                    if (!resp.ok) {{
                        status_el.innerHTML = "Failure!";
                        return;
                    }} else {{
                        status_el.innerHTML = "In progress";
                    }}
                }} catch(e) {{
                    status_el.innerHTML = "Failure!";
                    return;
                }}

                if (count === 100) {{
                    status_el.innerHTML = "Test complete";
                    return;
                }}

                setTimeout(check_url, 10);
            }}
            check_url();
            """
        )

    # ---------------------------------------------------------------------------------------------------
    # Page 2 - Comparing Metrics
    # ---------------------------------------------------------------------------------------------------

    @render_widget
    @reactive.event(input.select, input.checkbox_group, input.slider)
    def basic_plot():
        df = load_metrics(input.select())
        fig = make_basic_plot(df, input.checkbox_group(), input.slider())
        return fig

    @render_widget
    @reactive.event(input.select)
    def basic_bar_plot():
        df = load_metrics_bar(input.select())
        fig = make_basic_bar_plot(df, 10)
        return fig

    @render_widget
    @reactive.event(input.select, input.slider_bar_small)
    def basic_bar_plot_smaller():
        df = load_metrics_bar(input.select())
        min_val, max_val = input.slider_bar_small()
        df = df[(df["PHRED"] >= min_val) & (df["PHRED"] < max_val)]
        fig = make_basic_bar_plot(df, 1)
        return fig

    @render_widget
    @reactive.event(input.select)
    def basic_bar_plot_consequence_pathogenic():
        df = load_metrics_bar(input.select())
        fig = make_basic_bar_plot_consequence_pathogenic(df)
        return fig

    # ---------------------------------------------------------------------------------------------------
    # Page 3 - Compare
    # ---------------------------------------------------------------------------------------------------

    @render_widget
    @reactive.event(
        input.select_metric, input.checkbox_group_version_gr, input.slider_xaxis_compare
    )
    def compare_plot():
        metric = input.select_metric()
        fig = go.Figure()

        for version in input.checkbox_group_version_gr():
            df = load_metrics(version)
            if df is None:
                continue

            fig.add_trace(
                go.Scatter(x=df["Threshold"], y=df[metric], mode="lines", name=version)
            )

        fig.update_layout(
            title="Confusion Matrix Components vs. Thresholds",
            xaxis=dict(
                title="Threshold", showgrid=True, range=input.slider_xaxis_compare()
            ),
            yaxis=dict(title="Metrics", showgrid=True),
            template="simple_white",
            legend=dict(title="Metrics"),
            width=800,
            height=500,
        )

        return fig

    # ---------------------------------------------------------------------------------------------------
    # Page 4 - Genes
    # ---------------------------------------------------------------------------------------------------

    @render.text
    def missing_genes():
        data = load_metrics_bar(input.select_version_gr_genes())
        df = data.copy()
        genes = genes_from_list_or_file(input.list_genes, input.file_genes)

        if df is None or df.empty:
            return "No dataset loaded for the selected version."

        if genes is None:
            if input.list_genes() and input.file_genes():
                return "You can either put a list in the text field or upload a file, not both."
            elif not input.list_genes() and not input.file_genes():
                return "You must input a gene list or upload a file."
            else:
                return "Something went wrong while processing your input."

        df_genes = set(df["GeneName"].astype(str).str.strip().str.upper())
        missing = set(genes) - df_genes

        if missing:
            return f"Genes not found in the CSV: {', '.join(sorted(missing))}"
        else:
            return "All genes were found in the CSV."

    # ---------------------------------------------------------------------------------------------------
    # Calculate the new metrics
    # ---------------------------------------------------------------------------------------------------

    @reactive.calc
    def filtered_data():
        data = load_metrics_bar(input.select_version_gr_genes())
        if "GeneName" not in data.columns:
            raise ValueError("The uploaded CSV must contain a 'gene' column.")

        data["GeneName"] = data["GeneName"].astype(str).str.strip()
        mask = data["GeneName"].apply(
            has_matching_gene(input.list_genes, input.file_genes)
        )
        df_filtered = data[mask].copy()

        return df_filtered

    def new_calculation_for_genes():
        df = filtered_data()
        return calculate_metrics(df)

    # ----------------------------------------------------------------------------------------------------------------------------------
    # Page 4 - Plots: Linear Plot with all metrics | the whole dataframe | Barplot for number of entries | Table for number of entries
    # ----------------------------------------------------------------------------------------------------------------------------------

    @render_widget
    @reactive.event(input.action_button_genes)
    def basic_plot_genes():
        df = new_calculation_for_genes()
        if df is None:
            return go.Figure()

        fig = go.Figure()

        for metric in df.columns:
            fig.add_trace(
                go.Scatter(x=df["Threshold"], y=df[metric], mode="lines", name=metric)
            )

        fig.update_layout(
            title="Confusion Matrix Components vs. Thresholds",
            xaxis=dict(title="Threshold", showgrid=True, range=input.slider()),
            yaxis=dict(title="Metrics", showgrid=True),
            template="simple_white",
            legend=dict(title="Metrics"),
            width=800,
            height=500,
        )

        return fig

    @reactive.Calc
    def data_frame_raw():
        df = filtered_data()
        genes = genes_from_list_or_file(input.list_genes, input.file_genes)

        if not genes:
            return pd.DataFrame({"Message": ["No Genes were given (yet)"]})
        elif input.radio_buttons_table() == "ClinVar":
            return df[
                [
                    "AlleleID",
                    "Type_x",
                    "Name",
                    "GeneID_x",
                    "GeneSymbol",
                    "Origin",
                    "OriginSimple",
                    "Chromosome",
                    "ReviewStatus",
                    "NumberSubmitters",
                    "VariationID",
                    "PositionVCF",
                    "ReferenceAlleleVCF",
                    "AlternateAlleleVCF",
                    "ClinicalSignificance",
                ]
            ]
        elif input.radio_buttons_table() == "CADD":
            return df.drop(
                columns=[
                    "AlleleID",
                    "Type_x",
                    "Name",
                    "GeneID_x",
                    "GeneSymbol",
                    "Origin",
                    "OriginSimple",
                    "ReviewStatus",
                    "NumberSubmitters",
                    "VariationID",
                    "ClinicalSignificance",
                ]
            )
        else:
            return df

    @render.data_frame
    @reactive.event(input.action_button_genes, input.radio_buttons_table)
    def data_frame_full():
        df = data_frame_raw()
        return render.DataGrid(df)

    @render.download(filename=lambda: f"{input.radio_buttons_table()}_annotations.csv")
    @reactive.event(input.action_button_genes)
    def export_button():
        df = data_frame_raw()
        buffer = StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        yield buffer.getvalue()

    @render_widget
    @reactive.event(input.action_button_genes)
    def basic_bar_plot_by_gene():

        data = filtered_data()
        if data is None or data.empty:
            return go.Figure()

        data["category"] = data["ClinicalSignificance"].apply(categorize_label)
        grouped = (
            data.groupby([data["GeneName"], "category"], observed=True)
            .size()
            .unstack(fill_value=0)
        )
        grouped = grouped.loc[grouped.sum(axis=1).sort_values(ascending=False).index]

        fig = go.Figure()
        colors = {
            "pathogenic": "#C44E52",
            "likely pathogenic": "#8172B2",
            "benign": "#55A868",
            "likely benign": "#CCB974",
            "unknown": "#4C72B0",
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
            title="Stacked Bar Chart by Gene and Clinical Significance",
            xaxis_title="Gene",
            yaxis_title="Count",
            legend_title="Clinical Significance",
            height=600,
            width=1000,
            xaxis_tickangle=-45,
        )

        return fig

    @render.data_frame
    @reactive.event(input.action_button_genes)
    def data_frame_together():
        data = filtered_data()

        data["category"] = data["ClinicalSignificance"].apply(categorize_label)
        grouped = (
            data.groupby([data["GeneName"], "category"], observed=True)
            .size()
            .unstack(fill_value=0)
        )
        grouped = grouped.loc[grouped.sum(axis=1).sort_values(ascending=False).index]
        grouped = grouped.reset_index()

        return render.DataGrid(grouped)
