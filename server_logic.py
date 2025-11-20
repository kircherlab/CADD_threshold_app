from shiny import reactive, render, ui
import starlette.responses
from shinywidgets import render_widget
from data_loader import load_metrics, load_metrics_bar
from modules.basic_plot import make_basic_plot
from modules.basic_bar_plot import make_basic_bar_plot
from modules.compare_basic_plot import make_compare_basic_plot
from modules.basic_bar_plot_by_consequence import make_basic_bar_plot_by_consequence
from modules.functions_server_helpers import (
    calculate_metrics,
    find_missing_genes,
    filtered_data_by_given_genes,
    make_data_frame_for_given_genes,
    make_data_frame_counting_label_occurences_by_genes,
    export_df_to_csv_string,
    get_column_as_gene_list

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
        fig = make_basic_bar_plot(df, 10, "standard")
        return fig

    @render_widget
    @reactive.event(input.select, input.slider_bar_small)
    def basic_bar_plot_smaller():
        # TODO: consider extracting the slider-based subsetting logic to a helper.
        df = load_metrics_bar(input.select())
        min_val, max_val = input.slider_bar_small()
        df = df[(df["PHRED"] >= min_val) & (df["PHRED"] < max_val)]
        fig = make_basic_bar_plot(df, 1, "standard")
        return fig

    @render_widget
    @reactive.event(input.select)
    def basic_bar_plot_by_consequence():
        df = load_metrics_bar(input.select())
        fig = make_basic_bar_plot_by_consequence(df)
        return fig

    # ---------------------------------------------------------------------------------------------------
    # Page 3 - Compare Metrics across different versions
    # ---------------------------------------------------------------------------------------------------

    @render_widget
    @reactive.event(input.select_metric, input.checkbox_group_version_gr, input.slider_xaxis_compare)
    def compare_plot():
        metric = input.select_metric()
        fig = make_compare_basic_plot(metric, input.checkbox_group_version_gr(), input.slider_xaxis_compare())
        return fig

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
        # TODO: metric-list construction could be a helper `get_metric_list(df)`
        # keeping the render function a single line.
        df = calculate_metrics(filtered_data())
        metrics_list = []
        for metric in df.columns:
            if metric == "Threshold":
                continue
            metrics_list.append(metric)
        fig = make_basic_plot(df, metrics_list, [0, 100])
        return fig

    @reactive.Calc
    def data_frame_raw():
        df = filtered_data()
        return make_data_frame_for_given_genes(df, input.list_genes, input.file_genes, input.radio_buttons_table)

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
        fig = make_basic_bar_plot(data, 10, "gene")
        return fig

    @render.data_frame
    @reactive.event(input.action_button_genes)
    def data_frame_together():
        data = filtered_data()
        grouped = make_data_frame_counting_label_occurences_by_genes(data)
        return render.DataGrid(grouped)

    @render.text
    def missing_genes_panel():
        data = load_metrics_bar(input.select_version_gr_genes_for_panels())
        return find_missing_genes(data, get_column_as_gene_list(input.selectize_a_gene_panel()), None)

    #@reactive.calc
    #def filtered_data_panel():
    #    data = load_metrics_bar(input.select_version_gr_genes())
     #   return filtered_data_by_given_genes(data, input.list_genes, input.file_genes)
