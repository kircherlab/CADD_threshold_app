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


def genes_from_list_or_file(list_genes, file_genes):
    try:
        if list_genes() and file_genes():
            return None
        if not list_genes() and not file_genes():
            return None

        if list_genes():
            genes = list_genes().replace(",", "\n").splitlines()
            return [gene.strip().upper() for gene in genes if gene.strip()]

        elif file_genes():
            file_info = file_genes()
            file_path = file_info[0]["datapath"]
            filename = file_info[0]["name"].lower()

            if filename.endswith(".tsv") or "\t" in open(file_path).read(1000):
                delimiter = "\t"
            elif ";" in open(file_path).read(1000):
                delimiter = ";"
            elif "\n" in open(file_path).read(1000):
                delimiter = "\n"
            else:
                delimiter = ","

            try:
                df = pd.read_csv(file_path, delimiter=delimiter, header=None)
            except Exception as e:
                return None

            genes = df.iloc[:, 0].dropna().astype(str).str.strip().str.upper().tolist()
            return genes

    except Exception as e:
        print(f"Unexpected Error in gene_list: {e}")
        return None


def has_matching_gene(gene_entry, list_genes, file_genes):
    genes = genes_from_list_or_file(list_genes, file_genes) or []
    gene_set = set(g.strip() for g in re.split(r"[;,\s]+", gene_entry) if g)
    return not set(genes).isdisjoint(gene_set)


def calculate_metrics(data: pd.DataFrame) -> pd.DataFrame:
    label_column = "ClinicalSignificance"

    data["ClinicalSignificance"] = (
        data["ClinicalSignificance"].str.contains("pathogenic", case=False, na=False)
    ).map({True: "pathogenic", False: "benign"})

    thresholds = np.arange(1, 100, step=1)
    data = data.sort_values("PHRED")

    rows = []

    for threshold in thresholds:
        current_benign = data["PHRED"] <= threshold

        data["binary_prediction"] = np.where(current_benign, "benign", "pathogenic")

        try:
            tn, fp, fn, tp = confusion_matrix(
                data[label_column],
                data["binary_prediction"],
                labels=["benign", "pathogenic"],
            ).ravel()
        except ValueError:
            tn = fp = fn = tp = 0

        precision = precision_score(
            data[label_column],
            data["binary_prediction"],
            pos_label="pathogenic",
            zero_division=0,
        )
        recall = recall_score(
            data[label_column],
            data["binary_prediction"],
            pos_label="pathogenic",
            zero_division=0,
        )
        f1 = f1_score(
            data[label_column],
            data["binary_prediction"],
            pos_label="pathogenic",
            zero_division=0,
        )
        f2 = (
            (5 * precision * recall) / (4 * precision + recall)
            if (precision + recall) > 0
            else 0
        )
        accuracy = accuracy_score(data[label_column], data["binary_prediction"])
        balanced_acc = balanced_accuracy_score(
            data[label_column], data["binary_prediction"]
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
