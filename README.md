# SCLab-App

Interactive single-cell analysis application.

This package provides:

- A Typer-based CLI with three launch modes:
  - `sclab-app`: Launch JupyterLab with auto-open option
  - `sclab-app-dashboard`: Launch the Voila dashboard
  - `sclab-app-server`: Start JupyterLab without opening a browser
- A post-install setup script that creates platform-specific launchers and default notebooks.

## Development

- Recommended env: Conda (see `environment-dev.yml`).
- Editable install for local development:

```bash
pip install -e .
```

- Run CLI:

```bash
sclab-app --help
sclab-app info
```
