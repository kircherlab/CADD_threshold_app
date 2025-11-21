from shiny import ui
from shinywidgets import output_widget
from pathlib import Path
import pandas as pd


def get_ui():
    head = ui.tags.head(
        # browser-friendly files: prefer favicon.ico or PNG in www/
        ui.tags.link(
            rel="icon",
            href="Website/www/IconCADDThresholdAnalysis.png",
            type="image/x-icon",
        ),
        ui.tags.link(
            rel="shortcut icon", href="Website/www/favicon.ico", type="image/x-icon"
        ),
    )

    navbar = ui.page_navbar(
        ui.nav_panel("About", layout_zero()),
        ui.nav_panel("Comparing Metrics", layout_one(), value="compmetr"),
        ui.nav_panel(
            "Comparing Versions and Genome Releases", layout_two(), value="compvergr"
        ),
        ui.nav_panel(
            "Calculation for specific Genes", layout_three(), value="specificgenes"
        ),
        ui.nav_panel("Gene Panels", layout_four(), value="genepanels"),
        title="CADD Thresholds Analysis",
    )

    # return head and navbar together so the head tag is placed into the HTML head,
    # and page_navbar children remain nav panels (avoids the get_value error)
    return ui.TagList(head, navbar)


def layout_zero():
    md_content = Path(Path(__file__).parent / "markdowns/about_text.md").read_text(
        encoding="utf-8"
    )
    return ui.markdown(md_content)


def layout_one():
    md_content = Path(
        Path(__file__).parent / "markdowns/comparing_metrics_text.md"
    ).read_text(encoding="utf-8")
    md_content2 = Path(Path(__file__).parent / "markdowns/distributions.md").read_text(
        encoding="utf-8"
    )
    return ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "select",
                "Choose version and genome release:",
                {
                    "1.7_GRCh38": "1.7 GRCh38",
                    "1.6_GRCh38": "1.6 GRCh38",
                    "1.7_GRCh37": "1.7 GRCh37",
                    "1.6_GRCh37": "1.6 GRCh37",
                },
                selected="1.7_GRCh38",
            ),
            ui.input_checkbox_group(
                "checkbox_group",
                "Choose metrics:",
                {
                    "FalsePositives": "False Positives",
                    "TruePositives": "True Positives",
                    "FalseNegatives": "False Negatives",
                    "TrueNegatives": "True Negatives",
                    "Recall": "Recall",
                    "Specifity": "Specifity",
                    "FalsePositiveRate": "False Positive Rate",
                    "Precision": "Precision",
                    "F1Score": "F1 Score",
                    "F2Score": "F2 Score",
                    "Accuracy": "Accuracy",
                    "BalancedAccuracy": "Balanced Accuracy",
                },
            ),
            ui.input_slider(
                "slider",
                "x-axis range for the line chart (metrics)",
                min=1,
                max=100,
                value=[1, 100],
            ),
            ui.input_slider(
                "slider_bar_small",
                "x-axis range for small-scaled variant distribution",
                min=1,
                max=100,
                value=[1, 100],
            ),
            open="open",
        ),
        ui.markdown(md_content),
        ui.page_fillable(
            ui.card(output_widget("basic_plot")),
            ui.markdown(md_content2),
            ui.navset_card_tab(
                ui.nav_panel(
                    "Distribution of variants in steps of  10",
                    output_widget("basic_bar_plot"),
                ),
                ui.nav_panel(
                    "Distribution of variants in steps of  1",
                    output_widget("basic_bar_plot_smaller"),
                ),
                ui.nav_panel(
                    "Distribution of pathogenic variants with their consequence",
                    output_widget("basic_bar_plot_consequence_pathogenic"),
                ),
            ),
        ),
    )


def layout_two():
    return ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "select_metric",
                "Choose the metric you want to compare:",
                {
                    "FalsePositives": "False Positives",
                    "TruePositives": "True Positives",
                    "FalseNegatives": "False Negatives",
                    "TrueNegatives": "True Negatives",
                    "Recall": "Recall",
                    "Specifity": "Specifity",
                    "FalsePositiveRate": "False Positive Rate",
                    "Precision": "Precision",
                    "F1Score": "F1 Score",
                    "F2Score": "F2 Score",
                    "Accuracy": "Accuracy",
                    "BalancedAccuracy": "Balanced Accuracy",
                },
            ),
            ui.input_checkbox_group(
                "checkbox_group_version_gr",
                "Choose version and genome release:",
                {
                    "1.7_GRCh38": "1.7 GRCh38",
                    "1.6_GRCh38": "1.6 GRCh38",
                    "1.7_GRCh37": "1.7 GRCh37",
                    "1.6_GRCh37": "1.6 GRCh37",
                },
            ),
            ui.input_slider(
                "slider_xaxis_compare", "x-axis range", min=1, max=100, value=[1, 100]
            ),
            open="open",
        ),
        ui.layout_columns(
            ui.card(output_widget("compare_plot")),
        ),
    )


def layout_three():
    md_content = Path(
        Path(__file__).parent / "markdowns/specific_genes_text.md"
    ).read_text(encoding="utf-8")
    return ui.page_fluid(
        ui.markdown(md_content),
        ui.accordion(
            ui.accordion_panel(
                "Choose Options",
                ui.layout_columns(
                    ui.input_select(
                        "select_version_gr_genes",
                        "Select the Genome Release and CADD Version:",
                        {
                            "1.7_GRCh38": "1.7 GRCh38",
                            "1.6_GRCh38": "1.6 GRCh38",
                            "1.7_GRCh37": "1.7 GRCh37",
                            "1.6_GRCh37": "1.6 GRCh37",
                        },
                    ),
                    ui.input_text_area("list_genes", "Put your genes as a list", ""),
                    ui.input_file(
                        "file_genes",
                        "Or: Upload your file with the genes as a list",
                        accept=[".csv", ".txt", ".tsv"],
                        multiple=False,
                        width="400px",
                    ),
                ),
                ui.input_action_button("action_button_genes", "Generate Metrics"),
                ui.output_text("missing_genes"),
            ),
            ui.accordion_panel(
                "Line Graph for comparing metrics",
                output_widget("basic_plot_genes")
            ),
            ui.accordion_panel(
                "Table with used entries from Clinvar",
                ui.input_radio_buttons(
                    "radio_buttons_table",
                    "Choose which annotations you want to look at:",
                    {
                        "CADD": "show only CADD annotations",
                        "ClinVar": "show only ClinVar annotations",
                        "allanno": "show all annotations",
                    },
                ),
                ui.download_button("export_button", "Export as csv"),
                ui.output_data_frame("data_frame_full"),
            ),
            ui.accordion_panel(
                "Bar Chart with the used variants/entries",
                output_widget("basic_bar_plot_by_gene"),
            ),
            ui.accordion_panel(
                "Table with a conclusion of the used entries from Clinvar",
                ui.output_data_frame("data_frame_together"),
                width=200,
            ),
            open=["Choose Options", "Line Graph for comparing metrics"],
        ),
    )


def layout_four():
    md_content = Path(
        Path(__file__).parent / "markdowns/gene_panels_text.md"
    ).read_text(encoding="utf-8")
    return ui.page_fluid(
        ui.markdown(md_content),
        ui.accordion(
            ui.accordion_panel(
                "Choose Options",
                ui.layout_columns(
                    ui.input_select(
                        "select_version_gr_genes_for_panels",
                        "Select the Genome Release and CADD Version:",
                        {
                            "1.7_GRCh38": "1.7 GRCh38",
                            "1.6_GRCh38": "1.6 GRCh38",
                            "1.7_GRCh37": "1.7 GRCh37",
                            "1.6_GRCh37": "1.6 GRCh37",
                        },
                    ),
                    # Populate selectize options from the panels CSV (panel names as options).
                    # Fallback to a small static list if the CSV is missing or can't be read.
                    ui.input_selectize(
                        "selectize_a_gene_panel",
                        "Select a gene panel below:",
                        (lambda: (
                            (lambda df: {name: name for name in df['Name'].dropna().astype(str).tolist()})(pd.read_csv(Path(__file__).parent / 'data' / 'paneldata' / 'panels_summary_2025-11-20.csv'))
                            if (Path(__file__).parent / 'data' / 'paneldata' / 'panels_summary_2025-11-20.csv').exists() else {"1A": "Choice 1A", "1B": "Choice 1B", "1C": "Choice 1C"}
                        ))(),
                    ),
                ),
                ui.input_action_button("action_button_generate_metrics_for_panels", "Generate Metrics"),
                ui.output_text("missing_genes_panel"),
            ),
            ui.accordion_panel(
                "Line Graph for comparing metrics",
                output_widget("basic_plot_genes_for_panels"),
            ),
            ui.accordion_panel(
                "Table with used entries from Clinvar",
                ui.input_radio_buttons(
                    "radio_buttons_table_for_panels",
                    "Choose which annotations you want to look at:",
                    {
                        "CADD": "show only CADD annotations",
                        "ClinVar": "show only ClinVar annotations",
                        "allanno": "show all annotations",
                    },
                ),
                ui.download_button("export_button_for_panel_table", "Export as csv"),
                ui.output_data_frame("data_frame_full_for_panels"),
            ),
            ui.accordion_panel(
                "Bar Chart with the used variants/entries",
                output_widget("basic_bar_plot_by_gene_for_panels"),
            ),
            ui.accordion_panel(
                "Table with a conclusion of the used entries from Clinvar",
                ui.output_data_frame("data_frame_together_for_panels"),
                width=200,
            ),
            open=["Choose Options", "Line Graph for comparing metrics"],
        ),
    )
