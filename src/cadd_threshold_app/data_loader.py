from functools import lru_cache
from pathlib import Path
import pandas as pd
import importlib.resources as pkg_resources


def package_data_dir() -> Path:
    try:
        # when installed or importable from source: package data dir
        pkg_dir = Path(pkg_resources.files("cadd_threshold_app").joinpath("data"))
        # If the package data dir exists and is not empty, use it.
        if pkg_dir.exists() and any(pkg_dir.iterdir()):
            return pkg_dir
    except Exception:
        pass
    # Fallback: when running from the repository root, use repo_root/data
    return Path(__file__).resolve().parents[2] / "data"


DATA_PATH = package_data_dir()


@lru_cache(maxsize=None)
def load_metrics(version):
    path = DATA_PATH / f"basic_{version}_ClinicalSignificance_PHRED_pathogenic_1_101_metrics.csv.gz"
    if not path.exists():
        raise FileNotFoundError(
            f"Metrics file not found: {path}\n"
            f"Expected metrics under: {DATA_PATH}\n"
            "Fix: place the generated metrics file there, or create a symlink from the repo 'data/' into the package data folder,\n"
            "or run the data generation scripts described in the README."
        )
    return pd.read_csv(path, low_memory=False)


@lru_cache(maxsize=None)
def load_metrics_bar(version):
    path = DATA_PATH / f"random_{version}_without_duplicates_renamed.csv.gz"
    if not path.exists():
        raise FileNotFoundError(
            f"Bar-plot metrics file not found: {path}\n"
            f"Expected metrics under: {DATA_PATH}\n"
            "Fix: place the generated random file there, or create a symlink from the repo 'data/' into the package data folder,\n"
            "or run the data generation scripts described in the README."
        )
    return pd.read_csv(path, low_memory=False)
