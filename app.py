import pandas as pd
from pathlib import Path
from shiny.express import input, render, ui
from shiny import App
from functools import partial
from shiny.ui import page_navbar
import plotly.express as px
from shinywidgets import output_widget, render_widget  
import plotly.graph_objects as go

metrics_16_GRCh37_1_101_df = pd.read_csv(Path(__file__).parent / "basic_1.6_GRCh37_ClinicalSignificance_PHRED_pathogenic_1_101_metrics.csv.gz") 
metrics_17_GRCh37_1_101_df = pd.read_csv(Path(__file__).parent / "basic_1.7_GRCh37_ClinicalSignificance_PHRED_pathogenic_1_101_metrics.csv.gz")
metrics_16_GRCh38_1_101_df = pd.read_csv(Path(__file__).parent / "basic_1.6_GRCh38_ClinicalSignificance_PHRED_pathogenic_1_101_metrics.csv.gz")
metrics_17_GRCh38_1_101_df = pd.read_csv(Path(__file__).parent / "basic_1.7_GRCh38_ClinicalSignificance_PHRED_pathogenic_1_101_metrics.csv.gz")

ui.page_opts(
    title="CADD Thresholds Analysis",  
    page_fn=partial(page_navbar, id="page"),  
)

with ui.nav_panel("One") as app_ui:  
    with ui.layout_sidebar():
        with ui.sidebar(open="open"):

            ui.input_select(  
                "select",  
                "Choose the version and genome release:",  
                {"16GRCh37": "1.6 GRCh37", "17GRCh37": "1.7 GRCh37", "16GRCh38": "1.6 GRCh38", "17GRCh38": "1.7 GRCh38"},  
            )  

            ui.input_checkbox_group(  
                "checkbox_group",  
                "Choose the metrics: ",  
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
                    "BalancedAccuracy": "Balanced Accuracy",

                },  
            )

            ui.input_slider("slider", "x-axis range", min=1, max=100, value=[1,100]) 
            ui.input_slider("slider2", "y-axis range", min=1, max=100, value=[1,100])

        
        @render_widget  
        def basic_plot(): 

            threshold_min, threshold_max = input.slider()

            for key in input.select():
                if key == "16GRCh37":
                    data = metrics_16_GRCh37_1_101_df
                elif key == "17GRCh37":
                    data = metrics_17_GRCh37_1_101_df
                elif key == "16GRCh38":
                    data = metrics_16_GRCh38_1_101_df
                else:
                    data = metrics_17_GRCh38_1_101_df           

            fig = go.Figure()

            for key in input.checkbox_group():
                label = key
                if label in data.columns:
                    fig.add_trace(go.Scatter(
                        x=data["Threshold"],
                        y=data[label],
                        mode='lines',
                        name=label
                    ))

            fig.update_layout(
                title='Confusion Matrix Components vs. Thresholds',
                xaxis= dict(title="Threshold", range=[threshold_min, threshold_max]),
                yaxis_title='Metrics',
                template='simple_white',
                legend=dict(title='Metrics'),
                width=800,
                height=500
            )

            return fig

        

with ui.nav_panel("Two"):  
    with ui.layout_sidebar():
        with ui.sidebar(open="open"):

            ui.input_select(  
                "select_metrics",  
                "Choose the version and genome release:",  
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
                    "BalancedAccuracy": "Balanced Accuracy",

                },   
            )  

            ui.input_checkbox_group(  
                "checkbox_group_version_gr",  
                "Choose the metrics: ",  
                 {"16GRCh37": "1.6 GRCh37", "17GRCh37": "1.7 GRCh37", "16GRCh38": "1.6 GRCh38", "17GRCh38": "1.7 GRCh38"},
            )

            ui.input_slider("slider_xaxis_compare", "x-axis range", min=1, max=100, value=[1,100]) 
            ui.input_slider("slider_yaxis_compare", "y-axis range", min=1, max=100, value=[1,100])

        @render_widget  
        def compare_plot(): 

            threshold_min, threshold_max = input.slider()

            for key in input.select_metrics():
                metric = key        

            fig = go.Figure()

            for key in input.checkbox_group_version_gr():
                if key == "16GRCh37":
                    data1 = metrics_16_GRCh37_1_101_df
                    fig.add_trace(go.Scatter(
                        x=data1["Threshold"],
                        y=data1[metric],
                        mode='lines',
                        name=key
                    ))
                if key == "17GRCh37":
                    data2 = metrics_17_GRCh37_1_101_df
                    fig.add_trace(go.Scatter(
                        x=data2["Threshold"],
                        y=data2[metric],
                        mode='lines',
                        name=key
                    ))
                if key == "16GRCh38":
                    data3 = metrics_16_GRCh38_1_101_df
                    fig.add_trace(go.Scatter(
                        x=data3["Threshold"],
                        y=data3[metric],
                        mode='lines',
                        name=key
                    ))
                if key == "17GRCh38":
                    data1 = metrics_17_GRCh38_1_101_df
                    fig.add_trace(go.Scatter(
                        x=data1["Threshold"],
                        y=data1[metric],
                        mode='lines',
                        name=key
                    ))

            fig.update_layout(
                title='Confusion Matrix Components vs. Thresholds',
                xaxis= dict(title="Threshold", range=[threshold_min, threshold_max]),
                yaxis_title='Metrics',
                template='simple_white',
                legend=dict(title='Metrics'),
                width=800,
                height=500
            )

            return fig


                    
 
    
    




