# Build and Release Guide for SCLab-App

This document explains how to develop, test, and build SCLab-App for local use and for distribution via Conda Constructor.

## 1) Prerequisites

- Conda or Mamba installed (recommended: mamba)
- Node.js is installed from conda (for JupyterLab extensions)
- Linux/macOS/Windows supported

## 2) Create the Dev Environment

```bash
# Create and activate the development environment
mamba env create -f environment-dev.yml  # or: conda env create -f environment-dev.yml
mamba activate sclab-app-dev             # or: conda activate sclab-app-dev
```

This environment mirrors the Constructor environment as closely as possible for reliable parity.

## 3) Install SCLab-App (editable)

```bash
# From repo root
pip install -e .
```

This installs console scripts:
- `sclab-app`
- `sclab-app-dashboard`
- `sclab-app-server`

## 4) Quick Smoke Tests

```bash
# Show environment and availability
sclab-app info

# Create default notebooks at ~/Documents/SCLab-App/
sclab-app init

# Launch JupyterLab (default port 8899)
sclab-app --no-browser  # or omit --no-browser to auto-open after a short delay

# Launch dashboard (default port 8866)
sclab-app-dashboard --no-browser

# Launch server-only (no browser, default port 8899)
sclab-app-server
```

Notes:
- You can change the Jupyter host/port, e.g., `--host 0.0.0.0 --port 9000`.
- The CLI checks for port availability and will prompt you to choose a different port if in use.

## 5) Packaging with Flit (optional)

If you want to build wheels/sdists:

```bash
python -m pip install flit
flit build
# Dist artifacts will appear in dist/
```

## 6) Building an Installer with Conda Constructor

Constructor reads a YAML configuration that describes the environment and post-install steps.

- File: `sclab_constructor_config.txt` (rename to `construct.yaml` before building)

Recommended layout for building:

```bash
cp sclab_constructor_config.txt construct.yaml
constructor .
# or specify output dir
constructor --output-dir installers .
```

Key fields used in the config:
- `channels`: conda-forge, bioconda
- `specs`: core dependencies (python, jupyterlab, scanpy, etc.)
- `pip`: installs `sclab` and `sclab-app` (this package) and CLI dependency `typer`
- `post_install`: `scripts/setup_sclab_app.py` (creates desktop launchers and default notebooks)
- `extra_files`: optional default notebooks/assets to include

After installation, users will have:
- Desktop/menu entries (platform-specific)
- Default notebooks in `~/Documents/SCLab-App/`
- Launchers for `SCLab-App`, `SCLab-App Dashboard`, and `SCLab-App Server`

## 7) Releasing a New Version

1. Update `src/sclab_app/__init__.py` `__version__` and `pyproject.toml` version.
2. Build wheel/sdist with Flit.
3. Publish to your desired index or distribute via Constructor installers.

## 8) Troubleshooting

- Missing Typer during dev: ensure `typer>=0.9.0` is installed in your env.
- JupyterLab/Voila not found: check that your environment includes them (`environment-dev.yml`).
- Port already in use: pass a different `--port`.
- Browser did not open: re-run with `--no-browser` or open the printed URL manually.
