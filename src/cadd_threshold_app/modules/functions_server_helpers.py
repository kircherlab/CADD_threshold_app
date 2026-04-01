import glob
import os
import re
import typing as _typing
from datetime import datetime
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from ..data_loader import get_data_path
from .read_genes_from_list_or_file_functions import genes_from_list_or_file

APP_ROOT = Path(__file__).resolve().parents[1]


def categorize_label(label):
    label_lower = str(label).lower()
    if (
        "pathogenic" in label_lower and "likely" not in label_lower
    ) or "pathogenic/likely risk allele" in label_lower:
        return "pathogenic"
    elif "likely pathogenic" in label_lower:
        return "likely pathogenic"
    elif "benign" in label_lower and "likely" not in label_lower:
        return "benign"
    elif "likely benign" in label_lower:
        return "likely benign"
    else:
        return "unknown"


# from a file for a row get column as list of genes
def get_column_as_gene_list(panel_name):
    # Load the most recent panels_summary_*.csv from configured data path
    pattern = str(get_data_path() / "paneldata" / "panels_summary_*.csv")
    matches = glob.glob(pattern)
    if not matches:
        print(f"Warning: no panels summary files found matching: {pattern}")
        return []

    panels_summary_path = max(matches, key=os.path.getmtime)
    try:
        df = pd.read_csv(panels_summary_path)
    except Exception as e:
        print(f"Warning: failed to read panels summary {panels_summary_path}: {e}")
        return []

    try:
        gene_list_str = df.loc[df["Name"] == panel_name, "Genes"].values[0]
        # split on common delimiters and normalize
        gene_list = [
            gene.strip().strip("[]'\"").upper()
            for gene in re.split(r"[;,]", str(gene_list_str))
            if gene.strip()
        ]
        return gene_list
    except Exception:
        return []


def get_paneldata_date(as_string: bool = True) -> _typing.Optional[str]:
    path_glob = str(get_data_path() / "paneldata" / "panels_summary_*.csv")
    files = glob.glob(path_glob)

    # prefer extracting date from filename
    for f in sorted(files, reverse=True):
        base = os.path.basename(f)
        m = re.search(r"panels_summary_(\d{4}-\d{2}-\d{2})\.csv", base)
        if m:
            try:
                dt = datetime.strptime(m.group(1), "%Y-%m-%d").date()
                return dt.isoformat() if as_string else dt
            except Exception:
                return None


def entry_has_matching_gene(gene_entry, list_genes, file_genes):
    genes = genes_from_list_or_file(list_genes, file_genes) or []
    # Coerce non-string values (e.g. float/NaN from CSVs) to empty/string
    try:
        if pd.isna(gene_entry):
            gene_entry_str = ""
        else:
            gene_entry_str = str(gene_entry)
    except Exception:
        gene_entry_str = str(gene_entry)

    gene_set = {g.strip() for g in re.split(r"[;,\s]+", gene_entry_str) if g}
    return not set(genes).isdisjoint(gene_set)


def find_missing_genes(data, list_genes, file_genes):
    df = data.copy()
    genes = genes_from_list_or_file(list_genes, file_genes)

    if df is None or df.empty:
        return "No dataset loaded for the selected version."

    if genes is None:
        if list_genes and file_genes:
            return "You can either put a list in the text field or upload a file, not both."
        elif not list_genes and not file_genes:
            return "You must input a gene list or upload a file."
        else:
            return "Something went wrong while processing your input."

    df_genes = set(df["GeneName"].astype(str).str.strip().str.upper())
    missing = set(genes) - df_genes

    if missing:
        return f"Genes not found in the used database: {', '.join(sorted(missing))} ------- Genes found: {', '.join(sorted(df_genes & set(genes)))}"
    else:
        return f"All genes were found in the used database. Genes: {', '.join(sorted(genes))}"


def filtered_data_by_given_genes(data, list_genes, file_genes):
    if "GeneName" not in data.columns:
        raise ValueError("The uploaded CSV must contain a 'gene' column.")

    data["GeneName"] = data["GeneName"].astype(str).str.strip()
    mask = data["GeneName"].apply(
        lambda gene_entry: entry_has_matching_gene(gene_entry, list_genes, file_genes)
    )
    df_filtered = data[mask].copy()

    return df_filtered


def calculate_metrics(data: pd.DataFrame) -> pd.DataFrame:
    """This function calculates various metrics at different PHRED score thresholds for the provided data"""

    data["ClinicalSignificance"] = data["ClinicalSignificance"].apply(categorize_label)

    # Create a binary ground-truth column for metric calculations. Map
    # 'likely pathogenic' -> 'pathogenic' and 'likely benign' -> 'benign'.
    # Any unknown/other labels are treated as 'benign' for the purposes of
    # these binary metrics (this mirrors the historical behavior of
    # mapping likely->pathogenic for metrics while preserving original labels
    # for display elsewhere).
    data["binary_truth"] = np.where(
        data["ClinicalSignificance"].isin(["pathogenic", "likely pathogenic"]),
        "pathogenic",
        "benign",
    )

    thresholds = np.arange(1, 100, step=1)
    data = data.sort_values("PHRED")

    rows = []

    # If there is no data after filtering, return rows of zeros for each threshold
    if data is None or data.empty:
        for threshold in thresholds:
            rows.append(
                {
                    "Threshold": int(threshold),
                    "TrueNegatives": 0,
                    "FalsePositives": 0,
                    "FalseNegatives": 0,
                    "TruePositives": 0,
                    "Precision": 0.0,
                    "Recall": 0.0,
                    "F1Score": 0.0,
                    "F2Score": 0.0,
                    "Accuracy": 0.0,
                    "BalancedAccuracy": 0.0,
                    "FalsePositiveRate": 0.0,
                    "Specificity": 0.0,
                }
            )
        return pd.DataFrame(rows)

    for threshold in thresholds:
        current_benign = data["PHRED"] <= threshold

        data["binary_prediction"] = np.where(current_benign, "benign", "pathogenic")

        # Defensive handling: if after creating binary arrays they are empty, set metrics to 0
        y_true = data["binary_truth"]
        y_pred = data["binary_prediction"]

        if y_true.size == 0 or y_pred.size == 0:
            tn = fp = fn = tp = 0
            precision = recall = f1 = f2 = accuracy = balanced_acc = 0.0
            specificity = fpr = 0.0
        else:
            try:
                tn, fp, fn, tp = confusion_matrix(
                    y_true, y_pred, labels=["benign", "pathogenic"]
                ).ravel()
            except ValueError:
                tn = fp = fn = tp = 0

            precision = precision_score(
                y_true, y_pred, pos_label="pathogenic", zero_division=0
            )
            recall = recall_score(
                y_true, y_pred, pos_label="pathogenic", zero_division=0
            )
            f1 = f1_score(y_true, y_pred, pos_label="pathogenic", zero_division=0)
            f2 = (
                (5 * precision * recall) / (4 * precision + recall)
                if (precision + recall) > 0
                else 0
            )
            accuracy = accuracy_score(y_true, y_pred)
            balanced_acc = balanced_accuracy_score(y_true, y_pred)
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

        rows.append(
            {
                "Threshold": int(threshold),
                "TrueNegatives": int(tn),
                "FalsePositives": int(fp),
                "FalseNegatives": int(fn),
                "TruePositives": int(tp),
                "Precision": float(precision),
                "Recall": float(recall),
                "F1Score": float(f1),
                "F2Score": float(f2),
                "Accuracy": float(accuracy),
                "BalancedAccuracy": float(balanced_acc),
                "FalsePositiveRate": float(fpr),
                "Specificity": float(specificity),
            }
        )

    result_df = pd.DataFrame(rows)
    return result_df


def make_data_frame_for_given_genes(
    df: pd.DataFrame, list_genes, file_genes, radio_buttons_table
):
    genes = genes_from_list_or_file(list_genes, file_genes)

    if not genes:
        return pd.DataFrame(
            {"Message": ["Could not find any genes in the file or text."]}
        )

    if not isinstance(df, pd.DataFrame):
        return pd.DataFrame({"Message": ["No data available"]})

    choice = str(radio_buttons_table or "").lower()

    if choice == "clinvar":
        desired = [
            "AlleleID",
            "Type_ClinVar",
            "Name",
            "GeneID_ClinVar",
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
        cols = [c for c in desired if c in df.columns]
        return df[cols].copy()
    elif choice == "cadd":
        to_drop = [
            "AlleleID",
            "Type_ClinVar",
            "Name",
            "GeneID_ClinVar",
            "GeneSymbol",
            "Origin",
            "OriginSimple",
            "ReviewStatus",
            "NumberSubmitters",
            "VariationID",
            "ClinicalSignificance",
        ]
        return df.drop(
            columns=[c for c in to_drop if c in df.columns], errors="ignore"
        ).copy()
    else:
        return df.copy()


def make_data_frame_counting_label_occurences_by_genes(df: pd.DataFrame):
    data = df
    data["category"] = data["ClinicalSignificance"].apply(categorize_label)
    grouped = (
        data.groupby([data["GeneName"], "category"], observed=True)
        .size()
        .unstack(fill_value=0)
    )
    grouped = grouped.loc[grouped.sum(axis=1).sort_values(ascending=False).index]
    grouped = grouped.reset_index()

    return grouped


def export_df_to_csv_string(df: pd.DataFrame, index: bool = False) -> str:
    """Return a CSV string for the provided DataFrame.

    Parameters
    - df: DataFrame to export
    - index: whether to include the index in the CSV (default False)

    Returns
    - CSV content as a str
    """
    buf = StringIO()
    df.to_csv(buf, index=index)
    buf.seek(0)
    return buf.getvalue()
