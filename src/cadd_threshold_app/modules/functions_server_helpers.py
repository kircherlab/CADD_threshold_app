import glob
import os
import re
import typing as _typing
from datetime import datetime
from functools import lru_cache
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

DEFAULT_SUPPORT_THRESHOLDS = {
    "pathogenic": {"n25": 30, "n50": 50, "n75": 80},
    "benign": {"n25": 30, "n50": 50, "n75": 80},
}


def _normalize_variant_class(value: str) -> str:
    label = str(value or "").strip().lower()
    if label in {"pathogenic", "path", "p"}:
        return "pathogenic"
    if label in {"benign", "ben", "b"}:
        return "benign"
    return label


def _parse_version_key(version_key: str) -> tuple[str, str]:
    """Split keys like 'GRCh38-v1.7' into genome release and CADD version."""
    if not version_key:
        return "", ""
    if "-" not in version_key:
        return str(version_key).strip(), ""
    genome_release, cadd_version = str(version_key).split("-", maxsplit=1)
    return genome_release.strip(), cadd_version.strip()


def _extract_thresholds_from_row(row: pd.Series) -> dict:
    threshold_map = {}
    for raw_key in ["n25", "n50", "n75", "n90"]:
        if raw_key in row.index and pd.notna(row[raw_key]):
            try:
                threshold_map[raw_key] = int(float(row[raw_key]))
            except Exception:
                continue
    return threshold_map


@lru_cache(maxsize=1)
def load_support_threshold_table() -> pd.DataFrame:
    """Load precomputed support thresholds from the configured data path.

    Expected file: support_thresholds.csv
    Optional TSV fallback: support_thresholds.tsv
    """
    candidate_paths = []

    try:
        data_path = get_data_path()
        candidate_paths.extend(
            [
                (data_path / "support_thresholds.csv", ","),
                (data_path / "support_thresholds.tsv", "\t"),
            ]
        )
    except Exception:
        # get_data_path can be unavailable in some local setups; use packaged fallback.
        pass

    candidate_paths.extend(
        [
            (APP_ROOT / "data" / "support_thresholds.csv", ","),
            (APP_ROOT / "data" / "support_thresholds.tsv", "\t"),
        ]
    )

    for path, sep in candidate_paths:
        if path.exists():
            return pd.read_csv(path, sep=sep, low_memory=False)

    return pd.DataFrame()


def get_support_thresholds(version_key: str, variant_class: str) -> dict:  # noqa: C901
    """Return n25/n50/n75 (and optional n90) for a version/class pair.

    The lookup tries common schema variants to keep metadata format flexible:
    - version_key + variant_class columns
    - genome_release + cadd_version + variant_class columns
    - variant_class-only rows
    """
    variant_class_norm = _normalize_variant_class(variant_class)
    fallback = DEFAULT_SUPPORT_THRESHOLDS.get(
        variant_class_norm,
        {"n25": 30, "n50": 50, "n75": 80},
    )

    try:
        table = load_support_threshold_table().copy()
    except Exception:
        return fallback

    if table.empty:
        return fallback

    table.columns = [str(c).strip().lower() for c in table.columns]

    row = None
    if {"version_key", "variant_class"}.issubset(table.columns):
        match = table[
            (table["version_key"].astype(str).str.strip() == str(version_key).strip())
            & (
                table["variant_class"].astype(str).str.strip().str.lower()
                == variant_class_norm
            )
        ]
        if not match.empty:
            row = match.iloc[0]

    if row is None and {"genome_release", "cadd_version", "variant_class"}.issubset(
        table.columns
    ):
        genome_release, cadd_version = _parse_version_key(version_key)
        match = table[
            (table["genome_release"].astype(str).str.strip() == genome_release)
            & (table["cadd_version"].astype(str).str.strip() == cadd_version)
            & (
                table["variant_class"].astype(str).str.strip().str.lower()
                == variant_class_norm
            )
        ]
        if not match.empty:
            row = match.iloc[0]

    if row is None and "variant_class" in table.columns:
        match = table[
            table["variant_class"].astype(str).str.strip().str.lower()
            == variant_class_norm
        ]
        if not match.empty:
            row = match.iloc[0]

    if row is None:
        return fallback

    thresholds = _extract_thresholds_from_row(row)
    if not {"n25", "n75"}.issubset(thresholds.keys()):
        return fallback
    return thresholds


def classify_support_level(
    count: int, thresholds: dict, strict_good: bool = False
) -> str:
    """Classify count into Low/Moderate/Good support using threshold metadata."""
    n25 = int(thresholds.get("n25", 30))
    good_cutoff_key = "n90" if strict_good and "n90" in thresholds else "n75"
    good_cutoff = int(thresholds.get(good_cutoff_key, thresholds.get("n75", 80)))

    if int(count) < n25:
        return "Low support"
    if int(count) < good_cutoff:
        return "Moderate support"
    return "Good support"


def combine_support_levels(pathogenic_level: str, benign_level: str) -> str:
    """Conservative combination rule for overall support."""
    levels = {str(pathogenic_level), str(benign_level)}
    if "Low support" in levels:
        return "Low support"
    if "Moderate support" in levels:
        return "Moderate support"
    return "Good support"


def build_support_summary(df: pd.DataFrame, version_key: str) -> dict:
    """Compute pooled support summary for selected genes/panels."""
    safe_df = df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()
    if not safe_df.empty and "ClinicalSignificance" in safe_df.columns:
        safe_df["category"] = safe_df["ClinicalSignificance"].apply(categorize_label)
    else:
        safe_df["category"] = "unknown"

    pathogenic_count = int(
        safe_df["category"].isin(["pathogenic", "likely pathogenic"]).sum()
    )
    benign_count = int(safe_df["category"].isin(["benign", "likely benign"]).sum())

    pathogenic_thresholds = get_support_thresholds(version_key, "pathogenic")
    benign_thresholds = get_support_thresholds(version_key, "benign")

    pathogenic_support = classify_support_level(pathogenic_count, pathogenic_thresholds)
    benign_support = classify_support_level(benign_count, benign_thresholds)
    overall_support = combine_support_levels(pathogenic_support, benign_support)

    return {
        "pathogenic_count": pathogenic_count,
        "benign_count": benign_count,
        "pathogenic_support": pathogenic_support,
        "benign_support": benign_support,
        "overall_support": overall_support,
        "pathogenic_thresholds": pathogenic_thresholds,
        "benign_thresholds": benign_thresholds,
    }


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
    if not panel_name:
        return []

    df = _load_latest_panels_summary_df()
    if df.empty:
        return []

    try:
        gene_list_str = df.loc[df["Name"] == panel_name, "Genes"].values[0]
    except Exception:
        return []

    # split on common delimiters and normalize
    gene_list = [
        gene.strip().strip("[]'\"").upper()
        for gene in re.split(r"[;,]", str(gene_list_str))
        if gene.strip()
    ]
    return gene_list


@lru_cache(maxsize=1)
def _latest_panels_summary_path() -> str:
    # Load the most recent panels_summary_*.csv from configured data path
    pattern = str(get_data_path() / "paneldata" / "panels_summary_*.csv")
    matches = glob.glob(pattern)
    if not matches:
        return ""

    return max(matches, key=os.path.getmtime)


@lru_cache(maxsize=1)
def _load_latest_panels_summary_df() -> pd.DataFrame:
    panels_summary_path = _latest_panels_summary_path()
    if not panels_summary_path:
        return pd.DataFrame()

    try:
        return pd.read_csv(panels_summary_path)
    except Exception as e:
        print(f"Warning: failed to read panels summary {panels_summary_path}: {e}")
        return pd.DataFrame()


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

    genes = genes_from_list_or_file(list_genes, file_genes) or []
    gene_lookup = {str(g).strip().upper() for g in genes if str(g).strip()}
    if not gene_lookup:
        return data.iloc[0:0].copy()

    split_genes = data["GeneName"].astype(str).str.upper().str.split(r"[;,\s]+")
    exploded = split_genes.explode()
    matched_indices = exploded[exploded.isin(gene_lookup)].index.unique()
    df_filtered = data.loc[matched_indices].copy()

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
            "CHROM",
            "ReviewStatus",
            "NumberSubmitters",
            "VariationID",
            "POS",
            "REF",
            "ALT",
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
