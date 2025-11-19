# Developer documentation

This file lists the main Python modules and a short description of their responsibilities. It is intended as developer-facing documentation to help contributors find the right place to make changes.

- `app.py` — Shiny app entrypoint; assembles UI and calls `server`.
- `server_logic.py` — Core Shiny server: reactive bindings, renderers and handlers. Keep this file small: prefer to extract pure logic into modules under `modules/`.
- `data_loader.py` — Functions to load precomputed metrics and bar-plot data for different versions/genome releases.

Modules (under `modules/`):

- `modules/functions_server_helpers.py` — Utilities for gene parsing, label categorization, filtering helpers and `calculate_metrics` (metric calculation over PHRED thresholds).
- `modules/read_genes_from_list_or_file_functions.py` — Functions to read gene lists from text input or uploaded files.
- `modules/basic_plot.py` — Factory producing the main line plots for metrics.
- `modules/basic_bar_plot.py` — Bar plot factories used across the app.
- `modules/compare_basic_plot.py` — Comparison plot factory for version/GR comparisons.
- `modules/basic_bar_plot_by_consequence.py` — Specialized bar plot grouped by consequence + pathogenicity.
- `modules/plot_handlers.py` — Small wrappers that accept plain values (DataFrame, lists) and call plot factories. Useful to keep `server()` thin and make plotting logic unit-testable. # TODO: not there yet

Other folders:

- `data/` — (not all files tracked) contains precomputed CSVs used by the app.
- `markdowns/` — Static text used in the UI pages (about, distributions, documentation, specific genes explanation).
- `www/` — any static frontend assets. # TODO: currently empty.

## How to add a new plot or page
1. Add the plotting logic as a pure function in `modules/` that receives plain values and returns a figure object.
2. Add a small wrapper in `modules/plot_handlers.py` if needed to normalize input values. # TODO: not there yet
3. Wire the render handler in `server_logic.py` to call the wrapper, evaluating Shiny inputs before passing values.

## Tests TODO
- Add pytest-style unit tests under `tests/` targeting pure functions in `modules/` (e.g. `modules/functions_server_helpers.py`, `modules/plot_handlers.py`).
