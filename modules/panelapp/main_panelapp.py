from retrieve_panel_id_and_version import fetch_all_panels_and_versions
from compare_csv_and_add_new_entries import compare_and_update_panel_data


def main_panelapp():
    fetch_all_panels_and_versions(
        pages=5,
        save_csv=True,
        csv_path="data/paneldata/panels_and_versions_summary.csv",
    )
    compare_and_update_panel_data("data/paneldata/panels_summary_2025-11-20.csv",
                                  "data/paneldata/panels_and_versions_summary.csv")


if __name__ == '__main__':
    main_panelapp()
