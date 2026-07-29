import fnmatch
import glob
import os
import re
import zipfile
from functools import lru_cache
from pathlib import Path

import pandas as pd


def _build_panel_metrics_zip_candidates(cadd_ver):
    """Return plausible zip base names for a CADD/genome selector value."""
    if not isinstance(cadd_ver, str):
        return []

    raw = cadd_ver.strip()
    if not raw:
        return []

    candidates = {raw}

    # UI currently provides values like "GRCh38-v1.7".
    m = re.fullmatch(r"(GRCh\d+)-v?(\d+(?:\.\d+)?)", raw)
    if m:
        genome, cadd_num = m.groups()
        candidates.add(f"{genome}-v{cadd_num}")
        candidates.add(f"{genome}_{cadd_num}")

    # Backward-compatible support for legacy values like "1.7_GRCh38".
    m = re.fullmatch(r"v?(\d+(?:\.\d+)?)_(GRCh\d+)", raw)
    if m:
        cadd_num, genome = m.groups()
        candidates.add(f"{genome}_{cadd_num}")
        candidates.add(f"{genome}-v{cadd_num}")

    return sorted(candidates)


@lru_cache(maxsize=32)
def _get_panel_metrics_zip_matches(cadd_ver):
    combo_candidates = _build_panel_metrics_zip_candidates(cadd_ver)
    if not combo_candidates:
        return tuple()

    output_dir = str(get_data_path() / "paneldata" / "panel_metrics")
    specific_matches = []
    for combo in combo_candidates:
        specific_zip_pattern = os.path.join(output_dir, "**", f"{combo}.zip")
        specific_matches.extend(glob.glob(specific_zip_pattern, recursive=True))

    return tuple(sorted(set(specific_matches)))


@lru_cache(maxsize=64)
def _get_zip_metrics_members(zip_path):
    try:
        with zipfile.ZipFile(zip_path, mode="r") as zf:
            members = [
                n
                for n in zf.namelist()
                if fnmatch.fnmatch(os.path.basename(n), "*_metrics*.csv")
            ]
    except Exception:
        return tuple()

    return tuple(sorted(members))


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
    specific_matches = _get_panel_metrics_zip_matches(cadd_ver)

    if not specific_matches:
        return None

    # try the newest specific combo zip first
    for zip_path in reversed(specific_matches):
        try:
            candidates = [
                n
                for n in _get_zip_metrics_members(zip_path)
                if fnmatch.fnmatch(os.path.basename(n), f"{safe_panel}_metrics*.csv")
            ]
            if candidates:
                with zipfile.ZipFile(zip_path, mode="r") as zf:
                    with zf.open(candidates[-1]) as f:
                        return pd.read_csv(f)
        except Exception:
            continue

    return None
