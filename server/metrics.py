from shiny import reactive, render_text, render
import plotly.graph_objects as go
from data_loader import load_metrics, load_metrics_bar
from shinywidgets import output_widget, render_widget 
import pandas as pd 
from pathlib import Path
import numpy as np
metrics_dict = load_metrics()
metrics_dict_bar = load_metrics_bar()
from sklearn.metrics import (
    confusion_matrix, precision_score, recall_score,
    f1_score, accuracy_score, balanced_accuracy_score
)
from data_processing import filtered_data


@reactive.calc
def calculate_metrics():
    label_column = "ClinicalSignificance"
    data = filtered_data()

    data["ClinicalSignificance"] = (
        data["ClinicalSignificance"].str.contains("pathogenic", case=False, na=False)
    ).map({True: 'pathogenic', False: 'benign'})

    thresholds = np.arange(1, 100, step=10)
    data = data.sort_values("PHRED")
    #cumulative_benign = pd.Series([False] * len(data), index=data.index)

    rows = []

    for threshold in thresholds:
        current_benign = data["PHRED"] <= threshold

        #cumulative_benign |= current_benign
        data["binary_prediction"] = np.where(current_benign, "benign", "pathogenic")
        
        try:
            tn, fp, fn, tp = confusion_matrix(
                data[label_column], data["binary_prediction"],
                labels=["benign", "pathogenic"]
            ).ravel()
        except ValueError:
            tn = fp = fn = tp = 0

        precision = precision_score(data[label_column], data["binary_prediction"], pos_label="pathogenic", zero_division=0)
        recall = recall_score(data[label_column], data["binary_prediction"], pos_label="pathogenic", zero_division=0)
        f1 = f1_score(data[label_column], data["binary_prediction"], pos_label="pathogenic", zero_division=0)
        f2 = (5 * precision * recall) / (4 * precision + recall) if (precision + recall) > 0 else 0
        accuracy = accuracy_score(data[label_column], data["binary_prediction"])
        balanced_acc = balanced_accuracy_score(data[label_column], data["binary_prediction"])
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

        rows.append({
            "Threshold": threshold,
            "TrueNegatives": tn,
            "FalsePositives": fp,
            "FalseNegatives": fn,
            "TruePositives": tp,
            "Precision": precision,
            "Recall": recall,
            "F1Score": f1,
            "F2Score": f2,
            "Accuracy": accuracy,
            "BalancedAccuracy": balanced_acc,
            "FalsePositiveRate": fpr,
            "Specificity": specificity
        })

    result_df = pd.DataFrame(rows)
    return result_df