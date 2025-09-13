#!/usr/bin/env python3
"""
SCLab-App post-installation setup script.
Creates cross-platform launchers and sets up default notebooks.
"""

import sys
import platform
import shutil
from pathlib import Path


def create_launcher_scripts():
    """Create platform-specific launcher scripts."""
    system = platform.system()
    
    print(f"Creating launchers for {system}...")
    
    if system == "Windows":
        create_windows_launchers()
    elif system == "Darwin":
        create_macos_launchers()
    else:
        create_linux_launchers()


def create_windows_launchers():
    """Create Windows .bat launcher scripts."""
    scripts_dir = Path(sys.prefix) / "Scripts"
    scripts_dir.mkdir(exist_ok=True)
    
    # Main SCLab-App launcher (JupyterLab with auto-browser)
    jupyter_bat = scripts_dir / "sclab-app.bat"
    jupyter_bat.write_text(f'''@echo off
setlocal enabledelayedexpansion

set "SCLAB_HOME=%USERPROFILE%\\Documents\\SCLab-App"
if not exist "%SCLAB_HOME%" mkdir "%SCLAB_HOME%"

echo Starting SCLab-App...
echo Opening JupyterLab in your default browser...
echo Navigate to: http://localhost:8899/lab
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%SCLAB_HOME%"

REM Start JupyterLab and wait a moment before opening browser
start /min cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8899/lab"
"{sys.executable}" -m jupyterlab --notebook-dir="%SCLAB_HOME%" --no-browser --port=8899 --allow-root

pause
''', encoding='utf-8')
    
    # Dashboard launcher (Voila)
    dashboard_bat = scripts_dir / "sclab-app-dashboard.bat"
    dashboard_bat.write_text(f'''@echo off
setlocal enabledelayedexpansion

set "SCLAB_HOME=%USERPROFILE%\\Documents\\SCLab-App"
if not exist "%SCLAB_HOME%" mkdir "%SCLAB_HOME%"

echo Starting SCLab-App Dashboard...
echo Opening dashboard in your default browser...
echo.
echo Press Ctrl+C to stop the dashboard
echo.

cd /d "%SCLAB_HOME%"

REM Check if dashboard notebook exists
if not exist "%SCLAB_HOME%\\dashboard.ipynb" (
    echo Dashboard notebook not found. Please ensure dashboard.ipynb exists in %SCLAB_HOME%
    pause
    exit /b 1
)

REM Start Voila and wait before opening browser
start /min cmd /c "timeout /t 4 /nobreak >nul && start http://localhost:8866"
"{sys.executable}" -m voila "%SCLAB_HOME%\\dashboard.ipynb" --port=8866 --enable_nbextensions=True --no-browser

pause
''', encoding='utf-8')
    
    # Server-only launcher
    server_bat = scripts_dir / "sclab-app-server.bat"
    server_bat.write_text(f'''@echo off
setlocal enabledelayedexpansion

set "SCLAB_HOME=%USERPROFILE%\\Documents\\SCLab-App"
if not exist "%SCLAB_HOME%" mkdir "%SCLAB_HOME%"

echo Starting SCLab-App Server...
echo Server will be available at: http://localhost:8899/lab
echo Open this URL manually in your browser
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%SCLAB_HOME%"
"{sys.executable}" -m jupyterlab --notebook-dir="%SCLAB_HOME%" --no-browser --port=8899 --allow-root

pause
''', encoding='utf-8')


def create_macos_launchers():
    """Create macOS .app bundles."""
    apps_dir = Path.home() / "Applications" / "SCLab-App"
    apps_dir.mkdir(exist_ok=True)
    
    # Main SCLab-App
    create_macos_app("SCLab-App", f'''#!/bin/bash
export SCLAB_HOME="$HOME/Documents/SCLab-App"
mkdir -p "$SCLAB_HOME"
cd "$SCLAB_HOME"

echo "Starting SCLab-App..."
osascript -e 'tell application "Terminal" to do script "cd \"$HOME/Documents/SCLab-App\"; echo \"Starting SCLab-App JupyterLab...\"; echo \"Opening browser in 3 seconds...\"; {sys.executable} -m jupyterlab --notebook-dir=\"$HOME/Documents/SCLab-App\" --port=8899 --no-browser"'

sleep 3
open http://localhost:8899/lab
''')
    
    # Dashboard
    create_macos_app("SCLab-App Dashboard", f'''#!/bin/bash
export SCLAB_HOME="$HOME/Documents/SCLab-App"
mkdir -p "$SCLAB_HOME"
cd "$SCLAB_HOME"

if [ ! -f "$SCLAB_HOME/dashboard.ipynb" ]; then
    osascript -e 'display alert "Dashboard notebook not found" message "Please ensure dashboard.ipynb exists in ~/Documents/SCLab-App"'
    exit 1
fi

echo "Starting SCLab-App Dashboard..."
{sys.executable} -m voila "$SCLAB_HOME/dashboard.ipynb" --port=8866 --no-browser &

sleep 3
open http://localhost:8866
''')
    
    # Server only
    create_macos_app("SCLab-App Server", f'''#!/bin/bash
export SCLAB_HOME="$HOME/Documents/SCLab-App"
mkdir -p "$SCLAB_HOME"
cd "$SCLAB_HOME"

osascript -e 'tell application "Terminal" to do script "cd \"$HOME/Documents/SCLab-App\"; echo \"SCLab-App Server starting...\"; echo \"Open http://localhost:8899/lab in your browser\"; {sys.executable} -m jupyterlab --notebook-dir=\"$HOME/Documents/SCLab-App\" --port=8899 --no-browser"'
''')


def create_macos_app(name, script_content):
    """Create a macOS .app bundle."""
    app_dir = Path.home() / "Applications" / "SCLab-App" / f"{name}.app"
    contents_dir = app_dir / "Contents"
    macos_dir = contents_dir / "MacOS"
    
    macos_dir.mkdir(parents=True, exist_ok=True)
    
    # Create executable script
    script_file = macos_dir / name.replace(" ", "").replace("-", "")
    script_file.write_text(script_content)
    script_file.chmod(0o755)
    
    # Create Info.plist
    bundle_id = f"org.umbibio.sclab-app.{name.lower().replace(' ', '').replace('-', '')}"
    plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{name}</string>
    <key>CFBundleDisplayName</key>
    <string>{name}</string>
    <key>CFBundleExecutable</key>
    <string>{name.replace(" ", "").replace("-", "")}</string>
    <key>CFBundleIdentifier</key>
    <string>{bundle_id}</string>
    <key>CFBundleVersion</key>
    <string>0.1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>0.1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
</dict>
</plist>'''
    
    (contents_dir / "Info.plist").write_text(plist_content)


def create_linux_launchers():
    """Create Linux .desktop files."""
    applications_dir = Path.home() / ".local/share/applications"
    applications_dir.mkdir(parents=True, exist_ok=True)
    
    # Main SCLab-App
    jupyter_desktop = applications_dir / "sclab-app.desktop"
    jupyter_desktop.write_text(f'''[Desktop Entry]
Version=1.0
Type=Application
Name=SCLab-App
GenericName=Single-Cell Analysis Lab
Comment=Interactive single-cell analysis toolkit
Exec=bash -c 'mkdir -p "$HOME/Documents/SCLab-App" && cd "$HOME/Documents/SCLab-App" && echo "Starting SCLab-App..." && (sleep 3 && xdg-open http://localhost:8899/lab) & {sys.executable} -m jupyterlab --notebook-dir="$HOME/Documents/SCLab-App" --port=8899 --no-browser'
Icon=sclab-app
Terminal=true
Categories=Science;Education;Development;
Keywords=single-cell;bioinformatics;jupyter;analysis;
StartupNotify=true
''')
    jupyter_desktop.chmod(0o755)
    
    # Dashboard
    dashboard_desktop = applications_dir / "sclab-app-dashboard.desktop"
    dashboard_desktop.write_text(f'''[Desktop Entry]
Version=1.0
Type=Application
Name=SCLab-App Dashboard
GenericName=SCLab Analysis Dashboard
Comment=SCLab-App streamlined dashboard interface
Exec=bash -c 'mkdir -p "$HOME/Documents/SCLab-App" && cd "$HOME/Documents/SCLab-App" && if [ -f "dashboard.ipynb" ]; then (sleep 3 && xdg-open http://localhost:8866) & {sys.executable} -m voila "dashboard.ipynb" --port=8866 --no-browser; else echo "Dashboard notebook not found"; read -p "Press Enter to continue..."; fi'
Icon=sclab-app
Terminal=true
Categories=Science;Education;
Keywords=single-cell;dashboard;analysis;
StartupNotify=true
''')
    dashboard_desktop.chmod(0o755)
    
    # Server only
    server_desktop = applications_dir / "sclab-app-server.desktop"
    server_desktop.write_text(f'''[Desktop Entry]
Version=1.0
Type=Application
Name=SCLab-App Server
GenericName=SCLab Server Only
Comment=Start SCLab-App server without opening browser
Exec=bash -c 'mkdir -p "$HOME/Documents/SCLab-App" && cd "$HOME/Documents/SCLab-App" && echo "Starting SCLab-App Server..." && echo "Open http://localhost:8899/lab in your browser" && {sys.executable} -m jupyterlab --notebook-dir="$HOME/Documents/SCLab-App" --port=8899 --no-browser'
Icon=sclab-app
Terminal=true
Categories=Science;Education;Development;
Keywords=single-cell;server;jupyter;
StartupNotify=true
''')
    server_desktop.chmod(0o755)


def setup_default_notebooks():
    """Copy default notebooks to user's SCLab-App directory."""
    print("Setting up default notebooks...")
    
    # Determine user's SCLab-App directory
    if platform.system() == "Windows":
        user_sclab_dir = Path.home() / "Documents" / "SCLab-App"
    else:
        user_sclab_dir = Path.home() / "Documents" / "SCLab-App"
    
    user_sclab_dir.mkdir(parents=True, exist_ok=True)
    
    # Source notebooks from package installation
    package_notebooks = Path(sys.prefix) / "share" / "sclab-app" / "notebooks"
    
    if package_notebooks.exists():
        print(f"Copying notebooks from {package_notebooks} to {user_sclab_dir}")
        for notebook in package_notebooks.glob("*.ipynb"):
            dest = user_sclab_dir / notebook.name
            if not dest.exists():  # Don't overwrite existing notebooks
                shutil.copy2(notebook, dest)
                print(f"  Created: {dest.name}")
            else:
                print(f"  Skipped: {dest.name} (already exists)")
    else:
        print(f"Package notebooks directory not found: {package_notebooks}")
        # Create a basic dashboard notebook if none exists
        create_basic_dashboard(user_sclab_dir)


def create_basic_dashboard(sclab_dir):
    """Create a basic dashboard notebook if none exists."""
    dashboard_path = sclab_dir / "dashboard.ipynb"
    
    if not dashboard_path.exists():
        print("Creating basic dashboard notebook...")
        
        basic_dashboard = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "# SCLab-App Dashboard\n",
                        "\n",
                        "Welcome to SCLab-App! This is your main analysis dashboard.\n",
                        "\n",
                        "## Getting Started\n",
                        "\n",
                        "1. Import your single-cell data\n",
                        "2. Run quality control and preprocessing\n",
                        "3. Perform dimensionality reduction and clustering\n",
                        "4. Explore your results with interactive visualizations"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Import SCLab and create the main widget\n",
                        "import sclab\n",
                        "\n",
                        "# Create the main SCLab widget\n",
                        "# This will be your main interface for single-cell analysis\n",
                        "app = sclab.SCLabDashboard()  # Adjust this based on your actual API\n",
                        "app"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.12.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        import json
        with open(dashboard_path, 'w') as f:
            json.dump(basic_dashboard, f, indent=2)


def main():
    """Main setup function."""
    print("Setting up SCLab-App...")
    print(f"Python executable: {sys.executable}")
    print(f"Installation prefix: {sys.prefix}")
    print(f"Platform: {platform.system()}")
    print()
    
    try:
        # Create launcher scripts
        create_launcher_scripts()
        
        # Set up default notebooks
        setup_default_notebooks()
        
        print()
        print("✅ SCLab-App setup completed successfully!")
        print()
        print("You can now launch SCLab-App using:")
        
        if platform.system() == "Windows":
            print("  • Start Menu → SCLab-App")
            print("  • Start Menu → SCLab-App Dashboard") 
            print("  • Start Menu → SCLab-App Server")
        elif platform.system() == "Darwin":
            print("  • ~/Applications/SCLab-App → SCLab-App.app")
            print("  • ~/Applications/SCLab-App → SCLab-App Dashboard.app")
            print("  • ~/Applications/SCLab-App → SCLab-App Server.app")
        else:
            print("  • Applications Menu → Science → SCLab-App")
            print("  • Applications Menu → Science → SCLab-App Dashboard")
            print("  • Applications Menu → Science → SCLab-App Server")
        
        print()
        print("Your notebooks are located in: ~/Documents/SCLab-App")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
