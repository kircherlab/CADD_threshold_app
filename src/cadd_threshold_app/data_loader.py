from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).parent / "data"


@lru_cache(maxsize=None)
def load_metrics(version):
    return pd.read_csv(
        DATA_PATH
        / f"basic_{version}_ClinicalSignificance_PHRED_pathogenic_1_101_metrics.csv.gz",
        low_memory=False,
    )


@lru_cache(maxsize=None)
def load_metrics_bar(version):
    return pd.read_csv(
        DATA_PATH / f"random_{version}_without_duplicates_renamed.csv.gz",
        low_memory=False,
    )
