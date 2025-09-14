#!/usr/bin/env bash
# SCLab-App post-install wrapper
# Uses the Python interpreter from the installed prefix to run setup_sclab_app.py
# Writes verbose logs to a file for troubleshooting in minimal environments (e.g., Docker)

set -euo pipefail

# Constructor sets PREFIX to the install location
PREFIX=${PREFIX:-}
if [[ -z "${PREFIX}" ]]; then
  echo "ERROR: PREFIX is not set. This script must be run by Constructor during install." >&2
  exit 1
fi

LOG_DIR="$PREFIX/var/log/sclab-app"
LOG_FILE="$LOG_DIR/post_install.log"
mkdir -p "$LOG_DIR"

# Resolve this script's directory (works even if invoked via absolute path)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Prefer the Python we just installed
PY_UNIX="$PREFIX/bin/python"
PY_WIN="$PREFIX/python.exe"   # Not used here; Windows runs a different installer path

{
  echo "==== SCLab-App post_install start ===="
  date -u
  echo "PREFIX=$PREFIX"
  echo "SCRIPT_DIR=$SCRIPT_DIR"
  echo "PATH=$PATH"

  if [[ -x "$PY_UNIX" ]]; then
    echo "Using Python: $PY_UNIX"
    "$PY_UNIX" -c "import sys,platform; print('Python', sys.version); print('Platform', platform.platform())"
    echo "Running setup_sclab_app.py..."
    "$PY_UNIX" "$PREFIX/setup_sclab_app.py"
  else
    echo "ERROR: Python interpreter not found at $PY_UNIX" >&2
    echo "Contents of $PREFIX/bin:" >&2
    ls -la "$PREFIX/bin" || true
    exit 1
  fi

  echo "==== SCLab-App post_install end ===="
} | tee -a "$LOG_FILE"

exit 0
