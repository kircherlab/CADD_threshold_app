import requests

headers = {'Accept': 'application/json'}


URL = "https://panelapp.genomicsengland.co.uk/api/v1"


r = requests.get(f"{URL}/panels/?page=1", headers=headers)

print(r.json()['count'])
print(len(r.json()['results']))

for panel in r.json()['results']:
    panel_id = panel['id']
    panel_name = panel['name']
    panel_version = panel['version']
    panel_url = f"{URL}/panels/{panel_id}/genes/"
    r = requests.get(panel_url, headers=headers)
    try:
        genes = [gene['gene_data']['gene_symbol'] for gene in r.json()['results']]
        print(f"Panel ID: {panel_id}, Name: {panel_name}, Version: {panel_version}, Genes: {len(genes)}")
    except requests.exceptions.JSONDecodeError:
        print(f"Failed to decode JSON for Panel ID: {panel_id}, Name: {panel_name}, Version: {panel_version}")
