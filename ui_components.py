from shiny import ui
from shinywidgets import output_widget  
from faicons import icon_svg

def get_ui():
    return ui.page_navbar(
        ui.nav_panel("About", layout_zero()),
        ui.nav_panel("Comparing Metrics", layout_one()),
        ui.nav_panel("Comparing versions and genome releases", layout_two()),
        ui.nav_panel("Genes", layout_three()),
        title="CADD Thresholds Analysis"
    )


def layout_zero():
    return "ideofw"

def layout_one():
    return ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "select", "Choose version and genome release:",
                {
                    "16GRCh37": "1.6 GRCh37", 
                    "17GRCh37": "1.7 GRCh37", 
                    "16GRCh38": "1.6 GRCh38", 
                    "17GRCh38": "1.7 GRCh38"
                },
            ),
            ui.input_checkbox_group(
                "checkbox_group", "Choose metrics:",
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
            ui.input_slider("slider", "x-axis range", min=1, max=100, value=[1,100]),
            open="open"
        ),
        ui.page_fillable(
            ui.layout_column_wrap(
                ui.card(
                    output_widget("basic_plot") #, icon=icon_svg("chart-line")),
                ),
                ui.card(
                    output_widget("basic_bar_plot")
                ),
                width=1/1
            ),
        ), 
        
    )

def layout_two():
    return ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "select_metric", "Choose the metric you want to compare:",
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
                    "BalancedAccuracy": "Balanced Accuracy"
                },
            ),
            ui.input_checkbox_group(
                "checkbox_group_version_gr", "Choose version and genome release:",
                {
                    "16GRCh37": "1.6 GRCh37", 
                    "17GRCh37": "1.7 GRCh37", 
                    "16GRCh38": "1.6 GRCh38", 
                    "17GRCh38": "1.7 GRCh38"
                },
            ),
            ui.input_slider("slider_xaxis_compare", "x-axis range", min=1, max=100, value=[1,100]),
            open="open"
        ), 
        ui.layout_columns(
            ui.card(
                output_widget("compare_plot")
            ),
        ),
    )

def layout_three():
    return ui.page_fluid(
                ui.accordion(  
                    ui.accordion_panel("Choose Options",
                                        ui.layout_columns(  
                                            ui.input_select(  
                                                "select_version_gr_genes",  
                                                "Select the Genome Release and CADD Version:",  
                                                {   "16GRCh37": "1.6 GRCh37", 
                                                    "17GRCh37": "1.7 GRCh37", 
                                                    "16GRCh38": "1.6 GRCh38", 
                                                    "17GRCh38": "1.7 GRCh38"
                                                },  
                                            ),  
                                            ui.input_text_area("list_genes", "Put your genes as a list", ""), 
                                            ui.input_file("file_genes", "Or: Upload your file with the genes as a list", accept=[".csv", ".txt", ".tsv"], multiple=False, width=400),
                                        ),
                                        ui.input_action_button("action_button_genes", "Generate Metrics"), 
                                        ui.output_text("missing_genes")
                    ),
                    ui.accordion_panel("Line Graph for comparing metrics",
                        output_widget("basic_plot_genes")
                    ),
                    ui.accordion_panel("Table with used entries from Clinvar",
                        ui.output_data_frame("data_frame_full")
                    ),
                    ui.accordion_panel("Bar Chart with the used variants/entries",
                        output_widget("basic_bar_plot_by_gene")
                    ),
                    ui.accordion_panel("Table with a conclusion of the used entries from Clinvar",
                        ui.output_data_frame("data_frame_together"),
                        width = 200,
                    )
                )
    )