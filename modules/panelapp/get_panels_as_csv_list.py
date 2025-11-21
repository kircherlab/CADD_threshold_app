from datetime import datetime
import pandas as pd
from panel_app_http_error_handling import (
    get_with_retries,
    headers,
    URL,
)

"""Fetch all gene panels from PanelApp API (PanelID, Name, Version, Genes, GeneCount, DateOfCheck) and save as CSV.
--> this is for first initial creation of the panel data csv file"""

panel_list = []
current_date = datetime.now().strftime("%Y-%m-%d")

for i in range(1, 6):
    page_url = f"{URL}/panels/?page={i}"
    r = get_with_retries(page_url, headers=headers)

    if r is None:
        continue

    try:
        page_json = r.json()
    except ValueError as e:
        print(f"Failed to decode JSON for page {i}: {e}")
        continue

    print(page_json.get("count"))
    print(len(page_json.get("results", [])))

    for panel in page_json.get("results", []):
        panel_id = panel["id"]
        panel_name = panel["name"]
        panel_version = panel["version"]
        panel_url = f"{URL}/panels/{panel_id}/genes/"
        r = get_with_retries(panel_url, headers=headers)
        if r is None:
            print(f"Skipping Panel ID: {panel_id} due to repeated request failures")
            continue
        try:
            genes = [
                gene["gene_data"]["gene_symbol"] for gene in r.json().get("results", [])
            ]
            panel_list.append(
                {
                    "PanelID": panel_id,
                    "Name": panel_name,
                    "Version": panel_version,
                    "Genes": genes,
                    "GeneCount": len(genes),
                    "DateOfCheck": current_date,
                }
            )
        except ValueError:
            print(
                f"Failed to decode JSON for Panel ID: {panel_id}, Name: {panel_name}, Version: {panel_version}"
            )

df_panel_list = pd.DataFrame(panel_list)
df_panel_list["Genes"] = df_panel_list["Genes"].apply(lambda lst: ";".join(lst))
df_panel_list.to_csv(f"data/paneldata/panels_summary_{current_date}.csv", index=False)
