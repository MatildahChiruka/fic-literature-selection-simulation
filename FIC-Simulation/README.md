# FIC Literature-Selection Simulation (Supplementary Material S1)

This repository contains the Python code and generated outputs for the illustrative simulation reported in Appendix A of the manuscript **“A Calculus Framework for Multi-Era Literature Integration”** (FIC framework; update this title if the submitted manuscript title differs).

## Purpose and scope

The simulation uses synthetic citation networks to compare five literature-selection strategies under specified assumptions and to measure recovery of planted citation lineage. It is an exploratory illustration of how selection strategies behave under simulated conditions. It is **not** an empirical validation of the FIC framework and does not establish that one strategy is universally superior.

## Contents

- `fic_sim.py` — simulation engine, synthetic citation-network generation, selection strategies, and evaluation functions.
- `run_demo.py` — small demonstration run for two illustrative parameter settings.
- `run_grid.py` — runs the 32-setting parameter grid with 80 simulated fields per setting (2,560 synthetic networks in total) and writes `grid_results.json`.
- `make_figure.py` — generates the exploratory figure and `results_table.csv` from the grid output.
- `make_figure_manuscript.py` — generates the manuscript figure (`fic_sim_manuscript.png`) and LaTeX rows (`manuscript_table_rows.tex`) from `grid_results.json`.
- `grid_results.json` — included output from the grid run using random seed 7.
- `results_table.csv` — tabular version of the included grid results.
- `requirements.txt` — Python package requirements.

## Requirements

- Python 3.10 or later is recommended.
- NumPy
- Matplotlib

No external citation database or private dataset is required; the networks used in these experiments are generated synthetically by the code.

## Reproduce the included results

Run these commands in a terminal from the repository directory.

1. Create and activate a virtual environment (recommended).

   **Windows (PowerShell):**

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

   **macOS/Linux:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. Run the quick demonstration:

   ```bash
   python run_demo.py
   ```

3. Re-run the full grid (this overwrites `grid_results.json`):

   ```bash
   python run_grid.py
   ```

4. Regenerate the manuscript figure and table rows:

   ```bash
   python make_figure_manuscript.py
   ```

   This writes `fic_sim_manuscript.png` and `manuscript_table_rows.tex` in the repository directory.

5. Optional: generate the exploratory figure and table:

   ```bash
   python make_figure.py
   ```

   This script uses `grid_results.json` and writes its figure/table outputs in the current directory.

## Simulation design

The grid varies field age (`T`), obliteration rate (`obl`), and fitness parameter (`fitness`). The full grid evaluates eight strategies: `Recent window`, `Recency-weighted`, `Top-cited`, `Random`, `Hybrid (naive)`, `FIC proxy`, `FIC v2 (long walk)`, and `FIC v2 (short walk)`. Each parameter setting uses 80 repetitions and seed 7. The manuscript figure script selects five strategies for its two plotted panels; the grid output contains all eight. The reported outputs include lineage coverage and related summary measures. See the manuscript Appendix A and comments in `fic_sim.py` for the precise operational definitions and assumptions.

The code's operational rules are simulation proxies, not a complete automated implementation of the conceptual FIC framework. Interpret results only in light of the stated synthetic assumptions.

## Reproducibility notes

- The included `grid_results.json` and `results_table.csv` are the outputs supplied with this code package.
- Re-running the scripts may update generated files in place.
- Figures may differ slightly across Matplotlib versions or platforms even when the underlying numeric results are unchanged.
- The random seeds and parameter settings are specified in the scripts.

## Citation and versioning

Please cite the archived release using its Zenodo DOI once the GitHub release has been archived. Add the final DOI to this section and to the manuscript's Supplementary Materials and Data Availability Statement before submission. The GitHub repository URL alone is not a substitute for the DOI of the archived version.

## License

Choose and add an appropriate open-source license before making the repository public. Do not leave the repository without a clear license if you intend others to reuse the code. Confirm that all authors agree to the selected license.
