from shiny import ui
from shinywidgets import output_widget  
from faicons import icon_svg

def get_ui():
    return ui.page_navbar(
        ui.nav_panel("Comparing Metrics", layout_one()),
        ui.nav_panel("Comparing versions and genome releases", layout_two()),
        title="CADD Thresholds Analysis"
    )

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
            ui.input_slider("slider2", "y-axis range", min=1, max=100, value=[1,100]),
            open="open"
        ),
        ui.page_fillable(
            ui.navset_card_tab(  
                ui.nav_panel("Main Plot", output_widget("basic_plot"), icon=icon_svg("chart-line")),
                ui.nav_panel("B", "Panel B content"),
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
                    "TruePositives": "True Poitives",  
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
            ui.input_slider("slider_yaxis_compare", "y-axis range", min=1, max=100, value=[1,100]),
            open="open"
        ), 
        output_widget("compare_plot")
    )
