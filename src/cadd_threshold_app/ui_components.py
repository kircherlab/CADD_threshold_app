import glob
import os
from pathlib import Path

import pandas as pd
from shiny import ui
from shinywidgets import output_widget

from .data_loader import get_data_path

APP_ROOT = Path(__file__).resolve().parents[0]
# Common choices for CADD version and genome release
VERSION_GR_CHOICES = {
    "GRCh38-v1.7": "1.7 GRCh38",
    "GRCh38-v1.6": "1.6 GRCh38",
    "GRCh37-v1.7": "1.7 GRCh37",
    "GRCh37-v1.6": "1.6 GRCh37",
}

def _load_panel_choices():
    """Find newest panels_summary_*.csv and return dict of panel name choices.

    Falls back to a small static dict when no file is found or read fails.
    """
    pattern = get_data_path() / "paneldata" / "panels_summary_*.csv"
    matches = glob.glob(str(pattern))
    if not matches:
        return {"1A": "Choice 1A", "1B": "Choice 1B", "1C": "Choice 1C"}

    newest = max(matches, key=os.path.getmtime)
    try:
        df = pd.read_csv(newest)
        names = df["Name"].dropna().astype(str).tolist()
        return {name: name for name in names}
    except Exception:
        return {"1A": "Choice 1A", "1B": "Choice 1B", "1C": "Choice 1C"}


def get_ui():
    navbar = ui.page_navbar(
        ui.nav_panel("About", layout_zero(), value="about"),
        ui.nav_panel("Comparing Metrics", layout_one(), value="compmetr"),
        ui.nav_panel(
            "Comparing Versions and Genome Releases", layout_two(), value="compvergr"
        ),
        ui.nav_panel(
            "Calculation for specific Genes", layout_three(), value="specificgenes"
        ),
        ui.nav_panel("Gene Panels", layout_four(), value="genepanels"),
        ui.nav_panel("Impressum", layout_five(), value="impressum"),
        title="CADD ThresholdApp",
    )

    footer = ui.tags.footer(
        ui.tags.a(
            "Impressum",
            href="#",
            onclick="document.querySelector('[data-value=impressum]').click(); return false;",
        ),
        style="text-align: center; padding: 10px; font-size: 0.9em; color: #666;",
    )
    # return head and navbar together so the head tag is placed into the HTML head,
    # and page_navbar children remain nav panels (avoids the get_value error)
    # Inline CSS from www/styles.css (fallback to link if file missing)
    css_path = APP_ROOT / "www" / "styles.css"
    if css_path.exists():
        css_text = css_path.read_text(encoding="utf-8")
        head = ui.tags.head(ui.tags.style(css_text))
    else:
        head = ui.tags.head(ui.tags.link(rel="stylesheet", href="/styles.css"))
    return ui.TagList(head, navbar, footer)


def layout_zero():
    md_content = (APP_ROOT / "markdowns/about_text.md").read_text(encoding="utf-8")
    return ui.div(ui.markdown(md_content), class_="content-container")


def layout_one():
    md_content = (APP_ROOT / "markdowns/comparing_metrics_text.md").read_text(
        encoding="utf-8"
    )
    md_content2 = (APP_ROOT / "markdowns/distributions.md").read_text(encoding="utf-8")
    return ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "select",
                "Choose version and genome release:",
                VERSION_GR_CHOICES,
                selected="GRCh38-v1.7",
            ),
            ui.input_checkbox_group(
                "checkbox_group_1",
                "Choose metrics (number of variants):",
                {
                    "FalsePositives": "False Positives",
                    "TruePositives": "True Positives",
                    "FalseNegatives": "False Negatives",
                    "TrueNegatives": "True Negatives",
                },
                selected=[
                    "FalsePositives",
                    "TruePositives",
                    "FalseNegatives",
                    "TrueNegatives",
                ],
            ),
            ui.input_checkbox_group(
                "checkbox_group_2",
                "Choose metrics (percentage):",
                {
                    "Recall": "Recall",
                    "Specificity": "Specificity",
                    "FalsePositiveRate": "False Positive Rate",
                    "Precision": "Precision",
                    "F1Score": "F1 Score",
                    "F2Score": "F2 Score",
                    "Accuracy": "Accuracy",
                    "BalancedAccuracy": "Balanced Accuracy",
                },
                selected=[
                    "Recall",
                    "Specificity",
                    "FalsePositiveRate",
                    "Precision",
                    "F1Score",
                    "F2Score",
                    "Accuracy",
                    "BalancedAccuracy",
                ],
            ),
            ui.input_slider(
                "slider",
                "x-axis range for the line chart (metrics)",
                min=1,
                max=100,
                value=[1, 100],
            ),
            open="open",
        ),
        ui.div(ui.markdown(md_content), class_="content-container"),
        ui.page_fillable(
            ui.card(output_widget("basic_plot_1")),
            ui.card(output_widget("basic_plot_2")),
            ui.div(ui.markdown(md_content2), class_="content-container"),
            ui.navset_card_tab(
                ui.nav_panel(
                    "Distribution of variants in steps of  10",
                    output_widget("basic_bar_plot"),
                ),
                ui.nav_panel(
                    "Distribution of variants in steps of  1",
                    ui.input_slider(
                        "slider_bar_small",
                        "x-axis range for small-scaled variant distribution",
                        min=0,
                        max=100,
                        value=[0, 100],
                    ),
                    output_widget("basic_bar_plot_smaller"),
                ),
                ui.nav_panel(
                    "Distribution of pathogenic variants with their consequence",
                    output_widget("basic_bar_plot_by_consequence"),
                ),
            ),
        ),
    )


def layout_two():
    md_content = (APP_ROOT / "markdowns/comparing.md").read_text(encoding="utf-8")
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
                    "Specificity": "Specificity",
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
                VERSION_GR_CHOICES,
                selected=["GRCh38-v1.7", "GRCh38-v1.6"],
            ),
            ui.input_slider(
                "slider_xaxis_compare", "x-axis range", min=1, max=100, value=[1, 100]
            ),
            open="open",
        ),
        ui.div(ui.markdown(md_content), class_="content-container"),
        ui.layout_columns(
            ui.card(output_widget("compare_plot")),
        ),
    )


def layout_three():
    md_content = (APP_ROOT / "markdowns/specific_genes_text.md").read_text(
        encoding="utf-8"
    )
    return ui.page_fluid(
        ui.div(ui.markdown(md_content), class_="content-container"),
        ui.accordion(
            ui.accordion_panel(
                "Choose Options",
                ui.layout_columns(
                    ui.input_select(
                        "select_version_gr_genes",
                        "Select the Genome Release and CADD Version:",
                        VERSION_GR_CHOICES,
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
                "Line Graph for comparing metrics", output_widget("basic_plot_genes")
            ),
            ui.accordion_panel(
                "Table with used entries from Clinvar",
                ui.input_radio_buttons(
                    "radio_buttons_table",
                    "Choose which annotations you want to look at:",
                    {
                        "CADD": "show only CADD annotations",
                        "Clinvar": "show only ClinVar annotations",
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
    md_content = (APP_ROOT / "markdowns/gene_panels_text.md").read_text(
        encoding="utf-8"
    )
    return ui.page_fluid(
        ui.div(ui.markdown(md_content), class_="content-container"),
        ui.accordion(
            ui.accordion_panel(
                "Choose Options",
                ui.layout_columns(
                    ui.input_select(
                        "select_version_gr_genes_for_panels",
                        "Select the Genome Release and CADD Version:",
                        VERSION_GR_CHOICES,
                    ),
                    # Populate selectize options from the panels CSV (panel names as options).
                    # Fallback to a small static list if the CSV is missing or can't be read.
                    ui.input_selectize(
                        "selectize_a_gene_panel",
                        "Select a gene panel below:",
                        _load_panel_choices(),
                    ),
                ),
                ui.input_action_button(
                    "action_button_generate_metrics_for_panels", "Generate Metrics"
                ),
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
                        "Clinvar": "show only ClinVar annotations",
                        "allanno": "show all annotations",
                    },
                ),
                ui.download_button("export_button_for_panels", "Export as csv"),
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


def layout_five():
    md_content = (APP_ROOT / "markdowns/impressum.md").read_text(encoding="utf-8")
    return ui.div(ui.markdown(md_content), class_="content-container")
