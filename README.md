# CADD Threshold APP

A Shiny-for-Python web application to explore and compare distributions of ClinVar
variants across different CADD PHRED-score thresholds, filter by gene lists or panels, and
export per-gene/per-panel or filtered annotation summaries. The app is primarily intended for investigating the score distribution of known pathogenic and bening variants for different CADD PHRED-score thresholds.

This README explains the repository layout, how to run the app locally (pip/conda).

**Highlights**
- Interactive visualizations of CADD PHRED-score distributions
- Compare distributions across CADD/ClinVar versions and genome builds
- Per-gene filtering (paste a list or upload a file) and exportable summaries
- Per-panel filtering using panels from PanelApp and exportable summaries

## Requirements
- Python 3.10+ (3.12 recommended)
- See `requirements.txt` or `environment.yml` for full dependencies
- Docker (optional) — a `Dockerfile` is included for containerized runs

## Installation

Using pip

```bash
git clone https://github.com/kircherlab/CADD_threshold_app.git
cd CADD_threshold_app
pip install -r requirements.txt
```

Using Conda

```bash
conda env create -f environment.yml -n CADD_threshold_app
conda activate CADD_threshold_app
```

## Run the app locally

From the repository root:

```bash
python -m shiny run --port 8080 --host 0.0.0.0 app.py
```

Then open http://localhost:8080 in your browser.

## Data overview

- `data/` - contains preprocessed tables, panel summaries and metrics used by the app.
  - `paneldata/` - CSVs summarizing panels and versions used by the UI
  - `panel_metrics/` - generated metrics stored by date/version

Notes:
- Large raw annotation files are typically not tracked in the repository. The app
  expects prepared/normalized CSV inputs - use https://github.com/coraleif/CADD_Threshold_Analysis_Snakemake to regenerate CSV inputs or use the `modules/panelapp/` utilities
  if you need to regenerate panel CSVs from PanelApp.

## Key files and modules
- `app.py` - Shiny app entrypoint and UI wiring
- `server_logic.py` - main server-side reactive logic and handlers
- `data_loader.py` - helpers to load and preprocess annotation tables
-  `ui_components.py` - UI
- `modules/` - plotting helpers, utilities and gene-list/panel parsing helpers
  - `basic_plot.py`, `basic_bar_plot.py`, `compare_basic_plot.py` - plotting factories
  - `functions_server_helpers.py`, `read_genes_from_list_or_file_functions.py` - utilities
  - `panelapp/` - scripts to interact with PanelApp (CSV generation, comparison)

## Development notes
- To extend plots: add a factory under `modules/` and register it in server logic
- To add data sources: update `data_loader.py` and ensure column names match the
  plotting/metric code paths
- Linting/tests: None included by default. Add unit tests for critical data parsing
  when making larger refactors.

## Docker 
- The included `Dockerfile` builds a minimal image running the app on port 8080.

## License & contact
- See `LICENSE` for licensing terms.
- For questions about data sources, interpretation, or contributions, contact the
  repository maintainers or open an issue.

