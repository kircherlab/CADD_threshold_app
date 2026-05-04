import fnmatch
import glob
import os
import re
import zipfile
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
        / f"{version}_ClinicalSignificance_PHRED_pathogenic_1_100_metrics.csv.gz"
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
    path = data_path / f"{version}_without_duplicates.csv.gz"
    if not path.exists():
        raise FileNotFoundError(
            f"Bar-plot metrics file not found: {path}\n"
            f"Expected metrics under: {data_path}\n"
            "Fix: place the generated random file there, or create a symlink from the repo 'data/' into the package data folder,\n"
            "or run the data generation scripts described in the README."
        )
    return pd.read_csv(path, low_memory=False)


@lru_cache(maxsize=None)
def load_panel_metrics_from_zip(panel_name, cadd_ver):
    """Load precomputed panel metrics from zip file or return None.

    This mirrors the loader semantics used elsewhere: it uses the configured
    `CADD_THRESHOLD_DATA_PATH` (via `get_data_path()`) and searches under
    `paneldata/panel_metrics` for a zip file matching the genome+CADD combo.
    """
    safe_panel = re.sub(r"[^0-9A-Za-z._-]", "_", str(panel_name).strip())
    output_dir = str(get_data_path() / "paneldata" / "panel_metrics")

    combo_folder = None
    if isinstance(cadd_ver, str) and "_" in cadd_ver:
        parts = cadd_ver.split("_")
        if len(parts) >= 2:
            cadd_short = parts[0]
            genome = parts[1]
            combo_folder = f"{genome}_{cadd_short}"

    if not combo_folder:
        return None

    specific_zip_pattern = os.path.join(output_dir, "**", f"{combo_folder}.zip")
    specific_matches = sorted(glob.glob(specific_zip_pattern, recursive=True))

    if not specific_matches:
        return None

    # try the newest specific combo zip first
    for zip_path in reversed(specific_matches):
        try:
            with zipfile.ZipFile(zip_path, mode="r") as zf:
                candidates = [
                    n
                    for n in zf.namelist()
                    if fnmatch.fnmatch(
                        os.path.basename(n), f"{safe_panel}_metrics*.csv"
                    )
                ]
                if candidates:
                    with zf.open(candidates[-1]) as f:
                        return pd.read_csv(f)
        except Exception:
            continue

    return None
