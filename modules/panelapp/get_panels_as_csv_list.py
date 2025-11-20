from datetime import datetime
import requests
import pandas as pd
import time
from requests.exceptions import RequestException

headers = {"Accept": "application/json"}
URL = "https://panelapp.genomicsengland.co.uk/api/v1"
panel_list = []


def get_with_retries(url, headers=None, max_retries=5, backoff_factor=1.0):
    """GET `url` with simple retry/backoff on 429 and transient errors.
    Returns a `requests.Response` or `None` if all retries fail.
    """
    attempt = 0
    while attempt < max_retries:
        try:
            resp = requests.get(url, headers=headers)
        except RequestException as e:
            wait = backoff_factor * (2**attempt)
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
                    wait = backoff_factor * (2**attempt)
            else:
                wait = backoff_factor * (2**attempt)

            print(
                f"Rate limited (429) for {url}. Waiting {wait}s (attempt {attempt + 1}/{max_retries})"
            )
            time.sleep(wait)
            attempt += 1
            continue

        # For other 5xx server errors, retry; for 4xx (other than 429) don't retry
        if 500 <= resp.status_code < 600:
            wait = backoff_factor * (2**attempt)
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
