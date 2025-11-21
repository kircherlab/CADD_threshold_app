from panel_app_http_error_handling import (
    get_with_retries,
    headers,
    URL,
)


def get_panel_info(panel_id, headers_override=None):
    """Return panel info for a single `panel_id`.

    Result keys: `PanelID`, `Name`, `Version`, `Genes` (list), `GeneCount` (int)
    Returns None on persistent failure.
    """
    hdrs = headers_override if headers_override is not None else headers

    # Get panel metadata
    meta_url = f"{URL}/panels/{panel_id}/"
    resp = get_with_retries(meta_url, headers=hdrs)
    if resp is None:
        print(f"Failed to fetch panel metadata for {panel_id}")
        return None
    try:
        meta = resp.json()
    except ValueError:
        print(f"Failed to decode panel metadata JSON for {panel_id}")
        return None

    name = meta.get("name")
    version = meta.get("version")

    # Get genes (may be paginated)
    genes = []
    gene_page_url = f"{URL}/panels/{panel_id}/genes/"
    while gene_page_url:
        r = get_with_retries(gene_page_url, headers=hdrs)
        if r is None:
            print(f"Failed to fetch genes for panel {panel_id}")
            break
        try:
            j = r.json()
        except ValueError:
            print(f"Failed to decode genes JSON for panel {panel_id}")
            break

        for g in j.get("results", []):
            symbol = g.get("gene_data", {}).get("gene_symbol")
            if symbol:
                genes.append(symbol)

        # follow pagination
        gene_page_url = j.get("next")

    return {
        "PanelID": panel_id,
        "Name": name,
        "Version": version,
        "Genes": genes,
        "GeneCount": len(genes),
    }
