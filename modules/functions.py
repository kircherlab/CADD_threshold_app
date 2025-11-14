import pandas as pd
import re
import numpy as np
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    balanced_accuracy_score,
)


class GeneInputError(Exception):
    """Raised when gene input parsing fails or input is ambiguous."""


class ReadFileError(Exception):
    """Raised when file can not be read or found"""


# Categorizes the label column into 4 different labels
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


# Read the input from a textfield or file for genes
# 1. guess_separator: Guess a simple separator from a sample string
# 2. read_genes_from_list_input: Convert a text input into a list of upper-case gene names
# 3. read_genes_from_file: Read the first column from an uploaded file descriptor and return a list of upper-case gene names
# 4. read_df_or_lines: Try to read a dataframe first; on failure, read plain lines.
# 5. genes_from_list_or_file: Return a list of gene symbols from either a text input or an uploaded file.


def read_genes_from_list_input(text):
    if text is None:
        return []
    genes = str(text).replace(",", "\n").splitlines()
    return [g.strip().upper() for g in genes if g and g.strip()]


def read_genes_from_file(file_val):
    """Try to read the first column from an uploaded file descriptor and
    return a list of upper-case gene names, or None on failure.
    """
    try:
        file_info = file_val[0]
        file_path = file_info.get("datapath") or file_info.get("path")
    except Exception:
        raise ReadFileError("Invalid uploaded file descriptor.")

    if not file_path:
        raise ReadFileError("Uploaded file descriptor missing 'datapath' or 'path'.")

    # otherwise sample a bit of the file to guess delimiter and fallback
    try:
        with open(file_path, "rb") as fh:
            sample_bytes = fh.read(4096)
        sample = sample_bytes.decode(errors="ignore")
    except Exception:
        raise ReadFileError("Could not read the beginning of the file.")

    # guess separator and delegate reading to helper
    sep = guess_separator(sample)
    return read_df_or_lines(file_path, sep)


def guess_separator(sample_text: str):
    """Guess a simple separator from a sample string."""
    if "\t" in sample_text:
        return "\t"
    if ";" in sample_text:
        return ";"
    if "," in sample_text:
        return ","
    if "\n" in sample_text:
        return "\n"
    if " " in sample_text:
        return " "
    return None


def read_df_or_lines(file_path: str, sep):
    """Try to read a dataframe first; on failure, read plain lines.
    Returns a list of upper-case strings or None on total failure.
    """
    try:
        if sep:
            df = pd.read_csv(file_path, delimiter=sep, header=None, engine="python")
        else:
            df = pd.read_csv(file_path, sep=None, header=None, engine="python")
        return df.iloc[:, 0].dropna().astype(str).str.strip().str.upper().tolist()
    except Exception:
        try:
            with open(file_path, "r", errors="ignore") as fh:
                lines = [ln.strip() for ln in fh if ln.strip()]
            return [ln.upper() for ln in lines]
        except Exception:
            raise ReadFileError("Reading the file failed.")


def genes_from_list_or_file(list_genes, file_genes):
    """Return a list of gene symbols from either a text input or an uploaded file.

    Raises GeneInputError on ambiguous input (both/none) or when file parsing fails.
    """
    list_val = list_genes() if callable(list_genes) else list_genes
    file_val = file_genes() if callable(file_genes) else file_genes

    # ambiguous: both provided or both empty
    if bool(list_val) == bool(file_val):
        return None

    if list_val:
        return read_genes_from_list_input(list_val)

    genes = read_genes_from_file(file_val)
    if genes is None or not genes:
        raise GeneInputError("Could not parse uploaded gene file or no genes found in the uploaded file.")
    return genes


def has_matching_gene(gene_entry, list_genes, file_genes):
    genes = genes_from_list_or_file(list_genes, file_genes) or []
    gene_set = set(g.strip() for g in re.split(r"[;,\s]+", gene_entry) if g)
    return not set(genes).isdisjoint(gene_set)


def calculate_metrics(data: pd.DataFrame) -> pd.DataFrame:

    data["ClinicalSignificance"] = (
        data["ClinicalSignificance"].apply(categorize_label)
    )

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

    for threshold in thresholds:
        current_benign = data["PHRED"] <= threshold

        data["binary_prediction"] = np.where(current_benign, "benign", "pathogenic")

        try:
            tn, fp, fn, tp = confusion_matrix(
                data["binary_truth"],
                data["binary_prediction"],
                labels=["benign", "pathogenic"],
            ).ravel()
        except ValueError:
            tn = fp = fn = tp = 0
        precision = precision_score(
            data["binary_truth"],
            data["binary_prediction"],
            pos_label="pathogenic",
            zero_division=0,
        )
        recall = recall_score(
            data["binary_truth"],
            data["binary_prediction"],
            pos_label="pathogenic",
            zero_division=0,
        )
        f1 = f1_score(
            data["binary_truth"],
            data["binary_prediction"],
            pos_label="pathogenic",
            zero_division=0,
        )
        f2 = (
            (5 * precision * recall) / (4 * precision + recall)
            if (precision + recall) > 0
            else 0
        )
        accuracy = accuracy_score(data["binary_truth"], data["binary_prediction"])
        balanced_acc = balanced_accuracy_score(
            data["binary_truth"], data["binary_prediction"]
        )
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

        rows.append(
            {
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
                "Specificity": specificity,
            }
        )

    result_df = pd.DataFrame(rows)
    return result_df


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
        return f"Genes not found in the CSV: {', '.join(sorted(missing))}"
    else:
        return f"All genes were found in the CSV. Genes: {', '.join(sorted(genes))}"


def filtered_data_genes(data, list_genes, file_genes):
    if "GeneName" not in data.columns:
        raise ValueError("The uploaded CSV must contain a 'gene' column.")

    data["GeneName"] = data["GeneName"].astype(str).str.strip()
    mask = data["GeneName"].apply(
        lambda gene_entry: has_matching_gene(
            gene_entry, list_genes, file_genes
        )
    )
    df_filtered = data[mask].copy()

    return df_filtered


def make_data_frame_raw(df: pd.DataFrame, list_genes, file_genes, radio_buttons_table):
    genes = genes_from_list_or_file(list_genes, file_genes)

    if not genes:
        return pd.DataFrame({"Message": ["Could not find any genes in the file or text."]})
    elif radio_buttons_table == "ClinVar":
        return df[
            [
                "AlleleID",
                "Type_x",
                "Name",
                "GeneID_x",
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
        ]
    elif radio_buttons_table == "CADD":
        return df.drop(
            columns=[
                "AlleleID",
                "Type_x",
                "Name",
                "GeneID_x",
                "GeneSymbol",
                "Origin",
                "OriginSimple",
                "ReviewStatus",
                "NumberSubmitters",
                "VariationID",
                "ClinicalSignificance",
            ]
        )
    else:
        return df


def make_data_frame_together(df: pd.DataFrame):
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
