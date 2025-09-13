# Default Notebooks for SCLab-App

This folder is packaged into the installer and will be copied to the user's environment under:

- $PREFIX/share/sclab-app/notebooks/

Your post-install script (`scripts/setup_sclab_app.py`) will then copy missing notebooks into the user's `~/Documents/SCLab-App/` directory on first run.

Suggested files to include here:
- `dashboard.ipynb` (Voila-ready main entry point)
- `tutorial.ipynb`
- `01_data_import.ipynb`
- `02_quality_control.ipynb`
- `03_preprocessing.ipynb`
- `04_dimensionality_reduction.ipynb`
- `05_clustering.ipynb`
- `06_differential_expression.ipynb`
- `07_advanced_analysis.ipynb`
- `08_visualization.ipynb`

For now, this is a placeholder. Add your curated notebooks when ready.
