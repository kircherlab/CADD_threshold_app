import os
# import sys

# Ensure repo root is on sys.path when running this file directly
# repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# if repo_root not in sys.path:
# sys.path.insert(0, repo_root)

from modules.functions_server_helpers import calculate_metrics, filtered_data_by_given_genes
from data_loader import load_metrics_bar
import pandas as pd
import re
import io
import zipfile
from datetime import date

"""Calculate panel metrics for all panels in the panels summary file and save to CSV files."""
panels_summary_path = os.path.join('data', 'paneldata', 'panels_summary_2025-11-20.csv')
panels_df = pd.read_csv(panels_summary_path)
version = date.today().strftime("%Y%m%d")
cadd_list = ['1.6_GRCh37', '1.6_GRCh38', '1.7_GRCh37', '1.7_GRCh38']

# Prepare output directory and ZIP file for this run
output_dir = os.path.join('data', 'paneldata', 'panel_metrics')
os.makedirs(output_dir, exist_ok=True)
zip_path = os.path.join(output_dir, f"panel_metrics_{version}.zip")

for item in cadd_list:
    data = load_metrics_bar(item)
    for _, row in panels_df.iterrows():
        panel_name = row.get('Name', '')
        # sanitize panel name to avoid creating subdirectories or invalid filenames
        safe_panel_name = re.sub(r"[^0-9A-Za-z._-]", "_", panel_name.strip())

        # create a ZIP per panel per cadd version and write the CSV inside it
        zip_filename = os.path.join(output_dir, f"{safe_panel_name}_metrics_{item}_{version}.zip")

        # If the zip already exists, skip creating/overwriting it
        if os.path.exists(zip_filename):
            print(f"Skipping '{zip_filename}' (already exists)")
            continue

        # handle missing/NaN Genes column values safely
        gene_list_raw = row.get('Genes', '')
        if pd.isna(gene_list_raw):
            continue
        else:
            gene_list_str = str(gene_list_raw)

        # split on common delimiters and strip surrounding characters
        gene_list = [gene.strip().strip("[]'\"").upper() for gene in re.split(r"[;,]", gene_list_str) if gene.strip()]

        if not gene_list:
            continue

        filtered_df = filtered_data_by_given_genes(data, gene_list, None)
        metrics_df = calculate_metrics(filtered_df)

        csv_buf = io.StringIO()
        metrics_df.to_csv(csv_buf, index=False)
        arcname = f"{safe_panel_name}_metrics_{item}_{version}.csv"
        with zipfile.ZipFile(zip_filename, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(arcname, csv_buf.getvalue())
        print(f"Wrote '{arcname}' into '{zip_filename}'")

