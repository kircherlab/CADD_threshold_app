import concurrent.futures
import multiprocessing
import os
import re
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd

from ...data_loader import get_data_path, load_metrics_bar
from ..functions_server_helpers import calculate_metrics, filtered_data_by_given_genes

APP_ROOT = Path(__file__).resolve().parents[2]

"""Calculate panel metrics for all panels in the panels summary file and save to CSV files."""


def get_combo_folder_name(item):
    parts = item.split("_")
    if len(parts) >= 2:
        cadd_ver = parts[0]
        genome = parts[1]
        return f"{genome}_{cadd_ver}"
    return re.sub(r"[^0-9A-Za-z._-]", "_", item)


def prepare_panel_tasks(panels_df, item, combo_dir):
    tasks = []
    for _, row in panels_df.iterrows():
        panel_name = row.get("Name", "")
        gene_list_raw = row.get("Genes", "")
        if pd.isna(gene_list_raw):
            continue
        gene_list_str = str(gene_list_raw)
        tasks.append((panel_name, gene_list_str, item, combo_dir))
    return tasks


def process_panels_for_combo(tasks, run_dir, combo_folder, combo_dir):
    max_workers = min(4, (multiprocessing.cpu_count() or 1))
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as exc:
        futures = {exc.submit(process_panel, t): t for t in tasks}
        for fut in concurrent.futures.as_completed(futures):
            csv_path, status, msg = fut.result()
            if status == "written":
                print(f"Wrote '{csv_path}'")
            elif status == "skipped":
                print(f"Skipping '{csv_path}' ({msg})")
            else:
                print(f"Failed '{csv_path}': {msg}")

    create_combo_zip(run_dir, combo_folder, combo_dir)


def process_panel(task):
    panel_name, gene_list_str, item_arg, combo_dir_arg = task
    safe_panel_name = re.sub(r"[^0-9A-Za-z._-]", "_", str(panel_name).strip())
    csv_filename = f"{safe_panel_name}_metrics.csv"
    csv_path = os.path.join(combo_dir_arg, csv_filename)

    # skip if already exists
    if os.path.exists(csv_path):
        return (csv_path, "skipped", "exists")

    # parse gene list
    gene_list = [
        gene.strip().strip("[]'\"").upper()
        for gene in re.split(r"[;,]", gene_list_str)
        if gene.strip()
    ]
    if not gene_list:
        return (csv_path, "skipped", "no_genes")

    try:
        data_local = load_metrics_bar(item_arg)
        filtered_df = filtered_data_by_given_genes(data_local, gene_list, None)
        metrics_df = calculate_metrics(filtered_df)
        metrics_df.to_csv(csv_path, index=False)
        return (csv_path, "written", None)
    except Exception as e:
        return (csv_path, "error", str(e))


def create_combo_zip(run_dir, combo_folder, combo_dir):
    try:
        if os.path.exists(combo_dir) and any(os.scandir(combo_dir)):
            zip_path = os.path.join(run_dir, f"{combo_folder}.zip")
            with zipfile.ZipFile(
                zip_path, mode="w", compression=zipfile.ZIP_DEFLATED
            ) as zf:
                for root, _, files in os.walk(combo_dir):
                    for fname in files:
                        full_path = os.path.join(root, fname)
                        rel_path = os.path.relpath(full_path, combo_dir)
                        arcname = os.path.join(combo_folder, rel_path)
                        zf.write(full_path, arcname=arcname)
            print(f"Created combo ZIP '{zip_path}'")
        else:
            print(f"No files to zip for '{combo_dir}'")
    except Exception as e:
        print(f"Failed to create combo ZIP for '{combo_dir}': {e}")


def run_calculate_panel_metrics(cadd_list=None):
    """Run the panels metrics calculation for available panels_summary CSV.

    This function locates the most recent `panels_summary_*.csv` under
    the data path, prepares output directories and processes panels for
    configured CADD/genome combos. Intended to be called from a main
    orchestration point (e.g. `main_panelapp`).
    """
    candidate_pattern = str(get_data_path() / "paneldata" / "panels_summary_*.csv")
    matches = []
    try:
        import glob

        matches = glob.glob(candidate_pattern)
    except Exception:
        matches = []

    if not matches:
        raise FileNotFoundError(f"No panels summary files found matching: {candidate_pattern}")

    # pick the most recently modified panels summary file
    panels_summary_path = max(matches, key=os.path.getmtime)
    panels_df = pd.read_csv(panels_summary_path)
    candidate_basename = os.path.basename(panels_summary_path)
    if cadd_list is None:
        cadd_list = ["GRCh37-v1.6", "GRCh38-v1.6", "GRCh37-v1.7", "GRCh38-v1.7"]

    match = re.search(r"(\d{4}-\d{2}-\d{2})", candidate_basename)
    if match:
        try:
            parsed = datetime.strptime(match.group(1), "%Y-%m-%d")
            version = parsed.strftime("%Y%m%d")
        except Exception:
            version = datetime.now().strftime("%Y%m%d")
    else:
        version = datetime.now().strftime("%Y%m%d")

    # Prepare output directory for this run (dated folder)
    output_dir = str(get_data_path() / "paneldata" / "panel_metrics")
    run_dir = os.path.join(output_dir, version)
    os.makedirs(run_dir, exist_ok=True)

    # get name for each folder and create the folder
    for item in cadd_list:
        combo_folder = get_combo_folder_name(item)
        combo_dir = os.path.join(run_dir, combo_folder)
        os.makedirs(combo_dir, exist_ok=True)

        tasks = prepare_panel_tasks(panels_df, item, combo_dir)
        if not tasks:
            continue

        process_panels_for_combo(tasks, run_dir, combo_folder, combo_dir)


if __name__ == "__main__":
    run_calculate_panel_metrics()
