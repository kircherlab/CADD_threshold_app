import pandas as pd
import os
import shutil
from datetime import datetime

try:
    # Prefer package relative import when used as module
    from .get_specific_panel_info import get_panel_info
except Exception:
    # Fallback when executed as a script
    from get_specific_panel_info import get_panel_info


def compare_and_update_panel_data(old_file_path, new_file_path):
    """Compare two CSVs (old, new) and update old_file_path in-place.

    Only fetches data from PanelApp when a panel is new or its version changed.
    """
    print("Creating backup of the old panel data file...")
    backup_dir = os.path.join(os.path.dirname(old_file_path), "backup")
    os.makedirs(backup_dir, exist_ok=True)
    backup_file_path = os.path.join(
        backup_dir, f"panels_summary_{datetime.now().strftime('%Y-%m-%d')}_backup.csv"
    )
    shutil.copy2(old_file_path, backup_file_path)
    print(f"Backup created at {backup_file_path}")

    df_old = pd.read_csv(old_file_path)
    print(f"Loaded old panel data from {old_file_path} with {len(df_old)} entries")
    df_new = pd.read_csv(new_file_path)
    print(f"Loaded new panel data from {new_file_path} with {len(df_new)} entries")

    # Work with PanelID as index for easy lookups
    df_old_idx = df_old.set_index("PanelID")
    df_new_idx = df_new.set_index("PanelID")

    additional_rows = []
    counter = 0

    for panel_id in df_new_idx.index:
        new_row = df_new_idx.loc[panel_id]
        print(f"Processing panel {counter + 1}/{len(df_new_idx)}: {panel_id}")
        counter += 1
        if panel_id in df_old_idx.index:
            old_row = df_old_idx.loc[panel_id]
            if str(new_row.get("Version")) != str(old_row.get("Version")):
                print(
                    f"Version changed for Panel {panel_id}: {old_row.get('Version')} -> {new_row.get('Version')}"
                )
                info = get_panel_info(panel_id)
                if info is not None:
                    df_old_idx.at[panel_id, "Version"] = info.get(
                        "Version", new_row.get("Version")
                    )
                    df_old_idx.at[panel_id, "Genes"] = ";".join(info.get("Genes", []))
                    df_old_idx.at[panel_id, "GeneCount"] = info.get(
                        "GeneCount", new_row.get("GeneCount", 0)
                    )
                    df_old_idx.at[panel_id, "DateOfCheck"] = datetime.now().strftime(
                        "%Y-%m-%d"
                    )
                else:
                    print(
                        f"Warning: failed to fetch panel info for {panel_id}; leaving entry unchanged"
                    )
            else:
                # same version -> update date of check
                df_old_idx.at[panel_id, "DateOfCheck"] = datetime.now().strftime(
                    "%Y-%m-%d"
                )
        else:
            # new panel: fetch info and add
            print(
                f"New panel found: {panel_id} (version {new_row.get('Version')}); fetching info"
            )
            info = get_panel_info(panel_id)
            if info is not None:
                additional_rows.append(
                    {
                        "PanelID": info["PanelID"],
                        "Name": info.get("Name", new_row.get("Name")),
                        "Version": info.get("Version", new_row.get("Version")),
                        "Genes": ";".join(info.get("Genes", [])),
                        "GeneCount": info.get("GeneCount", 0),
                        "DateOfCheck": datetime.now().strftime("%Y-%m-%d"),
                    }
                )
            else:
                # fallback: copy row from new CSV (ensure Genes is string)
                fallback_genes = new_row.get("Genes", "")
                additional_rows.append(
                    {
                        "PanelID": panel_id,
                        "Name": new_row.get("Name", ""),
                        "Version": new_row.get("Version", ""),
                        "Genes": (
                            fallback_genes
                            if isinstance(fallback_genes, str)
                            else ";".join(fallback_genes)
                        ),
                        "GeneCount": new_row.get("GeneCount", 0),
                        "DateOfCheck": datetime.now().strftime("%Y-%m-%d"),
                    }
                )

    # Append any new panels
    if additional_rows:
        df_add = pd.DataFrame(additional_rows).set_index("PanelID")
        df_old_idx = pd.concat([df_old_idx, df_add], sort=False)

    # Reset index and save
    df_final = df_old_idx.reset_index()
    df_final.to_csv(old_file_path, index=False)
    print(f"Panel data updated and saved to {old_file_path}")
