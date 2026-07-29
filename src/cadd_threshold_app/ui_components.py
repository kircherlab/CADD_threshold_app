import glob
import os
from pathlib import Path

import pandas as pd
from shiny import ui
from shinywidgets import output_widget

from .data_loader import get_data_path

APP_ROOT = Path(__file__).resolve().parents[0]
APP_TITLE = "CADD ThresholdApp"
SOURCE_URL = "https://github.com/kircherlab/CADD_threshold_app"
# Common choices for CADD version and genome release
VERSION_GR_CHOICES = {
    "GRCh38-v1.7": "1.7 GRCh38",
    "GRCh38-v1.6": "1.6 GRCh38",
    "GRCh37-v1.7": "1.7 GRCh37",
    "GRCh37-v1.6": "1.6 GRCh37",
}


def _page_assets():
    return ui.tags.head(
        ui.tags.link(rel="stylesheet", href="/www/styles.css"),
        ui.tags.link(rel="icon", type="image/svg+xml", href="/www/favicon.svg"),
        ui.tags.link(rel="alternate icon", href="/www/favicon.ico"),
    )


def _card(title: str, *children, classes: str = ""):
    return ui.card(
        ui.card_header(title),
        *children,
        class_=f"cadd-card {classes}".strip(),
    )


def _markdown_card(title: str, markdown_text: str, classes: str = ""):
    return _card(title, ui.markdown(markdown_text), classes=classes)


def _stacked_content(*children):
    return ui.div(*children, class_="cadd-stack")


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
        ui.nav_spacer(),
        ui.nav_control(
            ui.a("Source", href=SOURCE_URL, target="_blank", class_="nav-link")
        ),
        title=ui.tags.span(ui.tags.strong(APP_TITLE), class_="app-brand"),
        navbar_options=ui.navbar_options(bg="#003754", theme="dark"),
        fillable=True,
    )
    return ui.TagList(_page_assets(), navbar)


def layout_zero():
    md_content = (APP_ROOT / "markdowns/about_text.md").read_text(encoding="utf-8")
    md_content_2 = (APP_ROOT / "markdowns/about_text_2.md").read_text(encoding="utf-8")

    # Try to include dataset.md dynamically from the configured data path
    dataset_text = ""
    try:
        data_path = get_data_path()
        candidate = data_path / "about_dataset_text" / "dataset.md"
        if candidate.exists():
            dataset_text = candidate.read_text(encoding="utf-8")
    except Exception:
        # get_data_path may raise if env var not set; ignore and try repo data folder
        pass

    # Fallback to repository `data/about_dataset_text/dataset.md` if present
    if not dataset_text:
        repo_candidate = (
            APP_ROOT.parents[1] / "data" / "about_dataset_text" / "dataset.md"
        )
        if repo_candidate.exists():
            dataset_text = repo_candidate.read_text(encoding="utf-8")

    if dataset_text:
        # Append dataset content to the about text without modifying the original file
        md_content = md_content + "\n\n" + dataset_text + "\n\n" + md_content_2
    else:
        # If no dataset text found, just concatenate the two about texts
        md_content = md_content + "\n\n" + md_content_2

    return _stacked_content(_markdown_card("About this site", md_content))


def layout_one():
    md_content = (APP_ROOT / "markdowns/comparing_metrics_text.md").read_text(
        encoding="utf-8"
    )
    md_content2 = (APP_ROOT / "markdowns/distributions.md").read_text(encoding="utf-8")
    return ui.layout_sidebar(
        ui.sidebar(
            _card(
                "Metrics controls",
                ui.input_select(
                    "select",
                    "Choose version and genome release:",
                    VERSION_GR_CHOICES,
                    selected="GRCh38-v1.7",
                ),
                ui.input_checkbox_group(
                    "checkbox_group_1",
                    "Choose metrics to display:",
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
                    selected=[
                        "FalsePositives",
                        "TruePositives",
                        "FalseNegatives",
                        "TrueNegatives",
                    ],
                ),
                ui.input_slider(
                    "slider",
                    "x-axis range for the line chart (metrics)",
                    min=1,
                    max=100,
                    value=[1, 100],
                ),
            ),
            open="open",
            width=320,
        ),
        _stacked_content(
            _markdown_card("Performance metrics across CADD PHRED scores", md_content),
            _card("Threshold metrics", output_widget("basic_plot_1")),
            _markdown_card("Distributions", md_content2),
            ui.navset_card_tab(
                ui.nav_panel(
                    "Distribution in steps of 10",
                    output_widget("basic_bar_plot"),
                ),
                ui.nav_panel(
                    "Distribution in steps of 1",
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
                    "Pathogenic consequences",
                    output_widget("basic_bar_plot_by_consequence"),
                ),
            ),
        ),
    )


def layout_two():
    md_content = (APP_ROOT / "markdowns/comparing.md").read_text(encoding="utf-8")
    return ui.layout_sidebar(
        ui.sidebar(
            _card(
                "Comparison controls",
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
                    "slider_xaxis_compare",
                    "x-axis range",
                    min=1,
                    max=100,
                    value=[1, 100],
                ),
            ),
            open="open",
            width=320,
        ),
        _stacked_content(
            _markdown_card("Comparing CADD versions and genome release", md_content),
            _card(
                "Version comparison", output_widget("compare_plot"), classes="plot-card"
            ),
        ),
    )


def layout_three():
    md_content = (APP_ROOT / "markdowns/specific_genes_text.md").read_text(
        encoding="utf-8"
    )
    return ui.layout_sidebar(
        ui.sidebar(
            _card(
                "Gene inputs",
                ui.input_select(
                    "select_version_gr_genes",
                    "Select the Genome Release and CADD Version:",
                    VERSION_GR_CHOICES,
                ),
                ui.input_text_area("list_genes", "Put your genes as a list", ""),
                ui.input_file(
                    "file_genes",
                    "Or upload a gene list file",
                    accept=[".csv", ".txt", ".tsv"],
                    multiple=False,
                    width="100%",
                ),
                ui.input_action_button(
                    "action_button_genes",
                    "Generate metrics",
                    class_="btn-primary w-100",
                ),
                ui.output_text("missing_genes"),
            ),
            open="open",
            width=340,
        ),
        _stacked_content(
            _markdown_card("Metrics calculation for specific genes", md_content),
            _card(
                "Support",
                ui.output_ui("support_indicator_genes"),
            ),
            _card(
                "Metrics plot", output_widget("basic_plot_genes"), classes="plot-card"
            ),
            ui.navset_card_tab(
                ui.nav_panel(
                    "ClinVar entries",
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
                ui.nav_panel(
                    "Bar chart visualization of variants",
                    _card(
                        "ClinVar variants by gene",
                        output_widget("basic_bar_plot_by_gene"),
                        classes="plot-card",
                    ),
                ),
                ui.nav_panel(
                    "Summary",
                    _card(
                        "Used entries overview",
                        ui.output_data_frame("data_frame_together"),
                    ),
                ),
            ),
        ),
    )


def layout_four():
    md_content = (APP_ROOT / "markdowns/gene_panels_text.md").read_text(
        encoding="utf-8"
    )
    return ui.layout_sidebar(
        ui.sidebar(
            _card(
                "Panel inputs",
                ui.input_select(
                    "select_version_gr_genes_for_panels",
                    "Select the Genome Release and CADD Version:",
                    VERSION_GR_CHOICES,
                ),
                ui.input_selectize(
                    "selectize_a_gene_panel",
                    "Select a gene panel below:",
                    _load_panel_choices(),
                ),
                ui.input_action_button(
                    "action_button_generate_metrics_for_panels",
                    "Generate metrics",
                    class_="btn-primary w-100",
                ),
                ui.output_text("missing_genes_panel"),
            ),
            open="open",
            width=340,
        ),
        _stacked_content(
            _markdown_card(
                "Metrics Calculation for gene panels (from PanelApp)", md_content
            ),
            _card("Support", ui.output_ui("support_indicator_panels")),
            _card(
                "Metrics plot",
                output_widget("basic_plot_genes_for_panels"),
                classes="plot-card",
            ),
            ui.navset_card_tab(
                ui.nav_panel(
                    "ClinVar entries",
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
                ui.nav_panel(
                    "Bar chart visualization of variants",
                    _card(
                        "ClinVar variants by gene",
                        output_widget("basic_bar_plot_by_gene_for_panels"),
                        classes="plot-card",
                    ),
                ),
                ui.nav_panel(
                    "Summary",
                    _card(
                        "Used entries overview",
                        ui.output_data_frame("data_frame_together_for_panels"),
                    ),
                ),
            ),
        ),
    )


def layout_five():
    md_content = (APP_ROOT / "markdowns/impressum.md").read_text(encoding="utf-8")
    return _markdown_card("Impressum / Imprint", md_content)
