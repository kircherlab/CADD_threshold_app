from pathlib import Path

import starlette.responses
from shiny import reactive, render, ui
from shinywidgets import render_widget

from .data_loader import load_metrics, load_metrics_bar, load_panel_metrics_from_zip
from .modules.basic_bar_plot import make_basic_bar_plot
from .modules.basic_bar_plot_by_consequence import make_basic_bar_plot_by_consequence
from .modules.basic_plot import make_basic_plot
from .modules.compare_basic_plot import make_compare_basic_plot
from .modules.functions_server_helpers import (
    calculate_metrics,
    export_df_to_csv_string,
    filtered_data_by_given_genes,
    find_missing_genes,
    get_column_as_gene_list,
    make_data_frame_counting_label_occurences_by_genes,
    make_data_frame_for_given_genes,
)

APP_ROOT = Path(__file__).resolve().parents[0]


def _setup_health_check(output, render, ui, session):
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
        return ui.tags.script(f"""
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
            """)


def _setup_page2_metrics(input, render_widget, reactive, render):
    # ---------------------------------------------------------------------------------------------------
    # Page 2 - Comparing Metrics
    # ---------------------------------------------------------------------------------------------------

    @render_widget
    @reactive.event(input.select, input.checkbox_group_1, input.slider)
    def basic_plot_1():
        df = load_metrics(input.select())
        fig = make_basic_plot(
            df,
            input.checkbox_group_1(),
            input.slider(),
            "Metrics at different CADD PHRED score thresholds",
            "Metric Value",
            "PHRED Score Threshold",
            "Metrics",
        )
        return fig
    
    @render_widget
    @reactive.event(input.select, input.checkbox_group_2, input.slider)
    def basic_plot_2():
        df = load_metrics(input.select())
        fig = make_basic_plot(
            df,
            input.checkbox_group_2(),
            input.slider(),
            "Metrics at different CADD PHRED score thresholds",
            "Metric Value",
            "PHRED Score Threshold",
            "Metrics",
        )
        return fig

    @render_widget
    @reactive.event(input.select)
    def basic_bar_plot():
        df = load_metrics_bar(input.select())
        fig = make_basic_bar_plot(
            df,
            10,
            "standard",
            "Distribution of ClinVar variants from threshold 0 to 100 in steps of 10",
            "PHRED Score",
            "Number of variants",
            "Clinical Classification from ClinVar",
            [-1, 11],
        )
        return fig

    @render_widget
    @reactive.event(input.select, input.slider_bar_small)
    def basic_bar_plot_smaller():
        # TODO: consider extracting the slider-based subsetting logic to a helper.
        df = load_metrics_bar(input.select())
        min_val, max_val = input.slider_bar_small()
        fig = make_basic_bar_plot(
            df,
            1,
            "standard",
            f"Distribution of ClinVar variants from threshold {min_val} to {max_val} in steps of 1",
            "PHRED Score",
            "Number of variants",
            "Clinical Classification from ClinVar",
            [min_val - 1, max_val],
        )
        return fig

    @render_widget
    @reactive.event(input.select)
    def basic_bar_plot_by_consequence():
        df = load_metrics_bar(input.select())
        fig = make_basic_bar_plot_by_consequence(df)
        return fig


def _setup_page3_compare(input, render_widget, reactive):
    # ---------------------------------------------------------------------------------------------------
    # Page 3 - Compare Metrics across different versions
    # ---------------------------------------------------------------------------------------------------

    @render_widget
    @reactive.event(
        input.select_metric, input.checkbox_group_version_gr, input.slider_xaxis_compare
    )
    def compare_plot():
        metric = input.select_metric()
        fig = make_compare_basic_plot(
            metric,
            input.checkbox_group_version_gr(),
            input.slider_xaxis_compare(),
        )
        return fig


def _get_metric_list(df):  # noqa: C901
    """Extract metric list from dataframe, excluding 'Threshold' column."""
    metrics_list = []
    for metric in df.columns:
        if metric == "Threshold":
            continue
        metrics_list.append(metric)
    return metrics_list


def _setup_page4_genes(input, render_widget, reactive, render):
    # ---------------------------------------------------------------------------------------------------
    # Page 4 Top - Render text for the given files with genes and filter the data by the given genes
    # ---------------------------------------------------------------------------------------------------

    @render.text
    def missing_genes():
        data = load_metrics_bar(input.select_version_gr_genes())
        return find_missing_genes(data, input.list_genes, input.file_genes)

    @reactive.calc
    def filtered_data():
        data = load_metrics_bar(input.select_version_gr_genes())
        return filtered_data_by_given_genes(data, input.list_genes, input.file_genes)

    # -----------------------------------------------------------------------------------------------------
    # Page 4 - Plots: Linear Plot with all metrics | the whole dataframe | export df to csv|
    # Barplot for number of entries | Table for number of entries
    # -----------------------------------------------------------------------------------------------------

    @render_widget
    @reactive.event(input.action_button_genes)
    def basic_plot_genes():
        df = calculate_metrics(filtered_data())
        metrics_list = _get_metric_list(df)
        fig = make_basic_plot(
            df,
            metrics_list,
            [0, 100],
            "Metrics at different CADD PHRED score thresholds for given genes",
            "Metric Value",
            "PHRED Score Threshold",
            "Metrics",
        )
        return fig

    @reactive.Calc
    def data_frame_raw():
        df = filtered_data()
        return make_data_frame_for_given_genes(
            df, input.list_genes, input.file_genes, input.radio_buttons_table()
        )

    @render.data_frame
    @reactive.event(input.action_button_genes, input.radio_buttons_table)
    def data_frame_full():
        df = data_frame_raw()
        return render.DataGrid(df)

    @render.download(filename=lambda: f"{input.radio_buttons_table()}_annotations.csv")
    @reactive.event(input.action_button_genes)
    def export_button():
        df = data_frame_raw()
        csv_text = export_df_to_csv_string(df, index=False)
        yield csv_text

    @render_widget
    @reactive.event(input.action_button_genes)
    def basic_bar_plot_by_gene():
        data = filtered_data()
        fig = make_basic_bar_plot(
            data,
            10,
            "gene",
            "Distribution of ClinVar variants by gene",
            "Gene",
            "Number of variants",
            "Clinical Classification from ClinVar",
            [-1, 11],
        )
        return fig

    @render.data_frame
    @reactive.event(input.action_button_genes)
    def data_frame_together():
        data = filtered_data()
        grouped = make_data_frame_counting_label_occurences_by_genes(data)
        return render.DataGrid(grouped)


def _setup_page4_panels(input, render_widget, reactive, render):
    # -----------------------------------------------------------------------------------------------------
    # Page 4 Bottom - Render text for the given panel with genes and filter the data by the given genes
    # -----------------------------------------------------------------------------------------------------
    @render.text
    def missing_genes_panel():
        data = load_metrics_bar(input.select_version_gr_genes_for_panels())
        return find_missing_genes(
            data, get_column_as_gene_list(input.selectize_a_gene_panel()), None
        )

    @reactive.calc
    def filtered_data_panel():
        data = load_metrics_bar(input.select_version_gr_genes_for_panels())
        return filtered_data_by_given_genes(
            data, get_column_as_gene_list(input.selectize_a_gene_panel()), None
        )

    @render_widget
    @reactive.event(input.action_button_generate_metrics_for_panels)
    def basic_plot_genes_for_panels():
        panel_name = input.selectize_a_gene_panel() or ""
        cadd_ver = input.select_version_gr_genes_for_panels() or ""

        # Try to load precomputed metrics from zip (moved to data_loader)
        df = load_panel_metrics_from_zip(panel_name, cadd_ver)

        # Fallback: calculate metrics from filtered data if no precomputed file found
        if df is None:
            df = calculate_metrics(filtered_data_panel())

        metrics_list = _get_metric_list(df)
        fig = make_basic_plot(
            df,
            metrics_list,
            [0, 100],
            "Metrics at different CADD PHRED score thresholds for given gene panel",
            "Metric Value",
            "PHRED Score Threshold",
            "Metrics",
        )
        return fig

    @reactive.Calc
    def data_frame_raw_for_panels():
        df = filtered_data_panel()
        return make_data_frame_for_given_genes(
            df,
            get_column_as_gene_list(input.selectize_a_gene_panel()),
            None,
            input.radio_buttons_table_for_panels(),
        )

    @render.data_frame
    @reactive.event(
        input.action_button_generate_metrics_for_panels,
        input.radio_buttons_table_for_panels,
    )
    def data_frame_full_for_panels():
        df = data_frame_raw_for_panels()
        return render.DataGrid(df)

    @render.download(
        filename=lambda: f"{input.radio_buttons_table_for_panels()}_panel_annotations.csv"
    )
    @reactive.event(input.action_button_generate_metrics_for_panels)
    def export_button_for_panels():
        df = data_frame_raw_for_panels()
        csv_text = export_df_to_csv_string(df, index=False)
        yield csv_text

    @render_widget
    @reactive.event(input.action_button_generate_metrics_for_panels)
    def basic_bar_plot_by_gene_for_panels():
        data = filtered_data_panel()
        fig = make_basic_bar_plot(
            data,
            10,
            "gene",
            "Distribution of ClinVar variants by gene",
            "Gene",
            "Number of variants",
            "Clinical Classification from ClinVar",
            [-1, 11],
        )
        return fig

    @render.data_frame
    @reactive.event(input.action_button_generate_metrics_for_panels)
    def data_frame_together_for_panels():
        data = filtered_data_panel()
        grouped = make_data_frame_counting_label_occurences_by_genes(data)
        return render.DataGrid(grouped)


def server(input, output, session):
    _setup_health_check(output, render, ui, session)
    _setup_page2_metrics(input, render_widget, reactive, render)
    _setup_page3_compare(input, render_widget, reactive)
    _setup_page4_genes(input, render_widget, reactive, render)
    _setup_page4_panels(input, render_widget, reactive, render)
