import os
from functools import lru_cache
from pathlib import Path

import pandas as pd


@lru_cache(maxsize=1)
def get_data_path() -> Path:
    from_env = os.getenv("CADD_THRESHOLD_DATA_PATH")
    if from_env is None:
        raise OSError(
            "CADD_THRESHOLD_DATA_PATH environment variable is not set. Please set it to the directory containing the precomputed input CSV files."
        )
    return Path(from_env).expanduser().resolve()


@lru_cache(maxsize=None)
def load_metrics(version):
    data_path = get_data_path()
    path = (
        data_path
        / f"basic_{version}_ClinicalSignificance_PHRED_pathogenic_1_101_metrics.csv.gz"
    )
    if not path.exists():
        raise FileNotFoundError(
            f"Metrics file not found: {path}\n"
            f"Expected metrics under: {data_path}\n"
            "Fix: place the generated metrics file there, or create a symlink from the repo 'data/' into the package data folder,\n"
            "or run the data generation scripts described in the README."
        )
    return pd.read_csv(path, low_memory=False)


@lru_cache(maxsize=None)
def load_metrics_bar(version):
    data_path = get_data_path()
    path = data_path / f"random_{version}_without_duplicates_renamed.csv.gz"
    if not path.exists():
        raise FileNotFoundError(
            f"Bar-plot metrics file not found: {path}\n"
            f"Expected metrics under: {data_path}\n"
            "Fix: place the generated random file there, or create a symlink from the repo 'data/' into the package data folder,\n"
            "or run the data generation scripts described in the README."
        )
    return pd.read_csv(path, low_memory=False)
