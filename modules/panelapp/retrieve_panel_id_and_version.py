import pandas as pd
import os
from panel_app_http_error_handling import get_with_retries, headers, URL


def fetch_all_panels_and_versions(pages, save_csv, csv_path):
    """Fetch panel IDs and versions for the first `pages` pages.

    Returns a DataFrame with columns `PanelID` and `Version`.
    If `save_csv` is True the result is written to `csv_path`.
    """
    panel_list = []

    for i in range(1, pages + 1):
        page_url = f"{URL}/panels/?page={i}"
        r = get_with_retries(page_url, headers=headers)

        if r is None:
            continue

        try:
            page_json = r.json()
        except ValueError as e:
            print(f"Failed to decode JSON for page {i}: {e}")
            continue

        for panel in page_json.get("results", []):
            panel_id = panel.get("id")
            panel_version = panel.get("version")
            # Optionally verify genes endpoint is reachable, but we only need id+version here
            panel_list.append({"PanelID": panel_id, "Version": panel_version})

    df_panel_and_versions_list = pd.DataFrame(panel_list)
    if save_csv:
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        df_panel_and_versions_list.to_csv(csv_path, index=False)
    print(f"Fetched {len(df_panel_and_versions_list)} panels and versions")
    print(f"Wrote {len(df_panel_and_versions_list)} panel entries to {csv_path}")
    return df_panel_and_versions_list
