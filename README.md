# CADD Threshold APP
#### This web application investigates the score distribution of known pathogenic and bening variants for different CADD PHRED-score thresholds. The app was built with Shiny for Python and provides a framework for loading, processing and visualising data.

This repository contains a Shiny-for-Python web application that analyzes the distribution
of ClinVar variants across different CADD PHRED-score thresholds and provides interactive
visualizations and per-gene filtering.

This README explains how to set up, run and develop the application locally.

## Features
- Load preprocessed ClinVar + CADD annotation tables for multiple versions and genome builds
- Compare score distributions across versions and genome releases
- Filter the dataset by gene lists (paste or upload) and compute metrics across thresholds
- Export filtered annotations and view per-gene summaries

## Requirements
- Python 3.10+ (3.12 recommended)
- See `requirements.txt` or `environment.yml` for the full dependency list

## Quick setup (pip)
1. Clone the repo:

```bash
git clone https://github.com/kircherlab/CADD_threshold_app.git
cd CADD_threshold_app
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Alternatively, use Conda with the provided `environment.yml`:

```bash
conda env create -f environment.yml -n CADD_threshold_app
conda activate CADD_threshold_app
```

## Run the app locally

From the repository root:

```bash
python -m shiny run --port 8080 --host 0.0.0.0 app.py
```

Open http://localhost:8080 in your browser.

## Development notes
- The app entry point is `app.py` and server logic is implemented in `server_logic.py`.
- Data loading helpers are in `data_loader.py`.
- Gene parsing and small utilities are in `modules/functions_server_helpers.py` and `modules/read_genes_from_list_or_file_functions.py`.
- Plot factories live under `modules/` (e.g. `basic_plot.py`, `basic_bar_plot.py`).


## Project structure (high level)
- `app.py` - Shiny app entrypoint
- `server_logic.py` - reactive handlers and UI wiring
- `modules/` - plotting helpers, parsing utilities and helper modules
- `data/` - data files (not all may be tracked in repo)
- `markdowns/` - documentation and page texts used in the app
- `requirements.txt`, `environment.yml` - dependency manifests


## Contact / License
- See `LICENSE` in the repository for licensing information.
- For questions about the dataset and analysis, contact the repository maintainers.



