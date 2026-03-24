# CADD Threshold APP

[![DOI](https://zenodo.org/badge/1008289329.svg)](https://doi.org/10.5281/zenodo.18863535)
[![GitHub License](https://img.shields.io/github/license/kircherlab/CADD_threshold_app)](https://github.com/kircherlab/CADD_threshold_app/blob/master/LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/kircherlab/CADD_threshold_app)](https://github.com/kircherlab/CADD_threshold_app/releases/latest)
[![PyPI version](https://badge.fury.io/py/cadd-threshold-app.svg)](https://badge.fury.io/py/cadd-threshold-app)
[![Bioconda Version](https://img.shields.io/conda/vn/bioconda/cadd-threshold-app?label=bioconda)](https://bioconda.github.io/recipes/cadd-threshold-app/README.html)
[![Tests](https://github.com/kircherlab/CADD_threshold_app/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/kircherlab/CADD_threshold_app/actions/workflows/tests.yml)
[![GitHub Issues](https://img.shields.io/github/issues/kircherlab/CADD_threshold_app)](https://github.com/kircherlab/CADD_threshold_app/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/kircherlab/CADD_threshold_app)](https://github.com/kircherlab/CADD_threshold_app/pulls)


A Shiny-for-Python web application to explore and compare distributions of ClinVar
variants across different CADD PHRED-score thresholds, filter by gene lists or panels, and
export per-gene/per-panel or filtered annotation summaries. The app is primarily intended for investigating the score distribution of known pathogenic and benign variants for different CADD PHRED-score thresholds.

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

### Pre-compiled packages

Using conda

```bash
conda create -n cadd_threshold_app -c bioconda -c conda-forge cadd-threshold-app
conda activate cadd_threshold_app
cadd-threshold-app --data </path/to/data>
```

Using pip

```bash
pip install cadd-threshold-app
cadd-threshold-app --data </path/to/data>
```

### From source

```bash
git clone https://github.com/kircherlab/CADD_threshold_app.git
cd CADD_threshold_app
pip install .
cadd-threshold-app --data data
```

Install as package (editable, recommended for development)

```bash
pip install -e .
```

## Data preparation

TODO

## Run the app


Option A: run via the package entry point

This requires installing the project as a package (e.g. pip install -e .).

```bash
cadd-threshold-app --data </path/to/data>
```

Alternatively to the cli option `--data`, you can set the `CADD_THRESHOLD_APP_DATA_DIR` environment variable.

```bash
export CADD_THRESHOLD_APP_DATA_DIR=data
cadd-threshold-app
```

Further CLI options are available to configute host and port - run `cadd-threshold-app --help` for details.

Option B: run from the repository root. Please set the `CADD_THRESHOLD_APP_DATA_DIR` environment variable to point to your data directory (e.g. `data/` in the repository) before running.

```bash
export CADD_THRESHOLD_APP_DATA_DIR=data
python -m shiny run cadd_threshold_app.app:app
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
