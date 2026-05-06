from pathlib import Path

from cadd_threshold_app.modules.panelapp.compare_csv_and_add_new_entries import (
    compare_and_update_panel_data,
)
from cadd_threshold_app.modules.panelapp.retrieve_panel_id_and_version import (
    fetch_all_panels_and_versions,
)
from cadd_threshold_app.modules.panelapp.calculate_panel_metrics_and_save import (
    run_calculate_panel_metrics,
)
import glob
import os

APP_ROOT = Path(__file__).resolve().parents[4]


def main_panelapp():
    fetch_all_panels_and_versions(
        pages=5,
        save_csv=True,
        csv_path=str(
            APP_ROOT / "data" / "paneldata" / "panels_and_versions_summary.csv"
        ),
    )
    pattern = str(APP_ROOT / "data" / "paneldata" / "panels_summary_*.csv")
    matches = glob.glob(pattern)
    if not matches:
        raise FileNotFoundError(f"No panels summary files found: {pattern}")
    latest = max(matches, key=os.path.getmtime)
    other_csv_path = str(APP_ROOT / "data" / "paneldata" / "panels_and_versions_summary.csv")
    compare_and_update_panel_data(latest, other_csv_path)
    # After panels CSV is created/updated, run metrics calculation
    run_calculate_panel_metrics()


if __name__ == "__main__":
    main_panelapp()
