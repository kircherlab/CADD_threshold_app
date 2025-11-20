import requests
import pandas as pd
import time
import os
from requests.exceptions import RequestException

# Public constants for other modules to import without triggering network activity
headers = {"Accept": "application/json"}
URL = "https://panelapp.genomicsengland.co.uk/api/v1"


def get_with_retries(url, headers=None, max_retries=5, backoff_factor=1.0):
    """GET `url` with simple retry/backoff on 429 and transient errors.
    Returns a `requests.Response` or `None` if all retries fail.
    """
    attempt = 0
    while attempt < max_retries:
        try:
            resp = requests.get(url, headers=headers)
        except RequestException as e:
            wait = backoff_factor * (2 ** attempt)
            print(
                f"RequestException for {url}: {e}. Backing off {wait}s (attempt {attempt + 1}/{max_retries})"
            )
            time.sleep(wait)
            attempt += 1
            continue

        if resp.status_code == 200:
            return resp

        if resp.status_code == 429:
            # Honor Retry-After header when present, otherwise exponential backoff
            retry_after = resp.headers.get("Retry-After")
            if retry_after is not None:
                try:
                    wait = int(retry_after)
                except ValueError:
                    # could be a HTTP-date; fall back to exponential
                    wait = backoff_factor * (2 ** attempt)
            else:
                wait = backoff_factor * (2 ** attempt)

            print(
                f"Rate limited (429) for {url}. Waiting {wait}s (attempt {attempt + 1}/{max_retries})"
            )
            time.sleep(wait)
            attempt += 1
            continue

        # For other 5xx server errors, retry; for 4xx (other than 429) don't retry
        if 500 <= resp.status_code < 600:
            wait = backoff_factor * (2 ** attempt)
            print(
                f"Server error {resp.status_code} for {url}. Backing off {wait}s (attempt {attempt + 1}/{max_retries})"
            )
            time.sleep(wait)
            attempt += 1
            continue

        # Non-retryable status
        print(f"Request failed for {url}: {resp.status_code}")
        return resp

    print(f"Exceeded max retries for {url}")
    return None


def fetch_all_panels_and_versions(pages=5, save_csv=True, csv_path="data/paneldata/panels_and_versions_summary.csv"):
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
    return df_panel_and_versions_list


if __name__ == "__main__":
    df = fetch_all_panels_and_versions(pages=5, save_csv=True)
    print(f"Wrote {len(df)} panel entries to data/paneldata/panels_and_versions_summary.csv")
