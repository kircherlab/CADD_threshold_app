import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data"

def load_metrics():
    return{
        "16GRCh37": pd.read_csv(DATA_PATH / "basic_1.6_GRCh37_ClinicalSignificance_PHRED_pathogenic_1_101_metrics.csv.gz"),
        "17GRCh37": pd.read_csv(DATA_PATH / "basic_1.7_GRCh37_ClinicalSignificance_PHRED_pathogenic_1_101_metrics.csv.gz"),
        "16GRCh38": pd.read_csv(DATA_PATH / "basic_1.6_GRCh38_ClinicalSignificance_PHRED_pathogenic_1_101_metrics.csv.gz"),
        "17GRCh38": pd.read_csv(DATA_PATH / "basic_1.7_GRCh38_ClinicalSignificance_PHRED_pathogenic_1_101_metrics.csv.gz"),
    }

def load_metrics_bar():
    return{
        "16GRCh37": pd.read_csv(DATA_PATH / "random_1.6_GRCh37_without_duplicates.csv.gz", low_memory=False),
        "17GRCh37": pd.read_csv(DATA_PATH / "random_1.7_GRCh37_without_duplicates.csv.gz", low_memory=False),
        "16GRCh38": pd.read_csv(DATA_PATH / "random_1.6_GRCh38_without_duplicates.csv.gz", low_memory=False),
        "17GRCh38": pd.read_csv(DATA_PATH / "random_1.7_GRCh38_without_duplicates.csv.gz", low_memory=False),
    }