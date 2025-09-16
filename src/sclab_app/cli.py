#!/usr/bin/env python3
"""
SCLab-App command-line interface.
Provides entry points for different launch modes using Typer.
"""

import os
import sys
import time
import platform
import subprocess
import webbrowser
from pathlib import Path
import threading
from typing import Optional, Annotated
import socket

import typer


# Create the main Typer app
app = typer.Typer(
    name="sclab-app",
    help="🧬 SCLab-App: Interactive single-cell analysis toolkit",
    rich_markup_mode="rich",
    add_completion=False
)


def get_sclab_home() -> Path:
    """Get the SCLab-App home directory."""
    return Path.home() / "Documents" / "SCLab-App"


def ensure_sclab_home() -> Path:
    """Ensure SCLab-App home directory exists."""
    sclab_home = get_sclab_home()
    sclab_home.mkdir(parents=True, exist_ok=True)
    return sclab_home


def check_dashboard_notebook() -> bool:
    """Check if dashboard notebook exists."""
    sclab_home = get_sclab_home()
    dashboard_path = sclab_home / "dashboard.ipynb"
    return dashboard_path.exists()


def open_browser_delayed(url: str, delay: int = 3) -> None:
    """Open browser after a delay (non-blocking)."""
    def delayed_open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
        except Exception as e:
            typer.echo(f"Could not open browser automatically: {e}", err=True)
            typer.echo(f"Please open {url} manually in your browser.")
    
    thread = threading.Thread(target=delayed_open, daemon=True)
    thread.start()


def is_port_available(host: str, port: int) -> bool:
    """Return True if binding to (host, port) succeeds (i.e., port is available)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


@app.command()
def main(
    no_browser: Annotated[bool, typer.Option("--no-browser", help="Don't open browser automatically")] = False,
    port: Annotated[int, typer.Option("--port", min=1, max=65535, help="Port for JupyterLab server")] = 8899,
    host: Annotated[str, typer.Option("--host", help="Host/IP to bind the server (e.g., 127.0.0.1 or 0.0.0.0)")] = "127.0.0.1",
    open_delay: Annotated[int, typer.Option("--open-delay", min=0, max=60, help="Delay (seconds) before opening browser")] = 3,
    notebook_dir: Annotated[Optional[Path], typer.Option("--notebook-dir", help="Notebook directory")] = None,
) -> None:
    """
    🚀 Launch SCLab-App with JupyterLab (main interface).
    
    This is the primary way to use SCLab-App with the full JupyterLab environment.
    """
    # Set up environment
    sclab_home = notebook_dir or ensure_sclab_home()
    
    typer.echo("🧬 Starting SCLab-App...")
    typer.echo(f"📂 Notebook directory: {sclab_home}")
    display_host = host if host not in ("0.0.0.0", "::") else "localhost"
    typer.echo(f"🌐 Server URL: http://{display_host}:{port}/lab")
    
    # if not no_browser:
    #     typer.echo(f"🚀 Opening JupyterLab in your default browser in {open_delay} seconds...")
    #     open_browser_delayed(f"http://{display_host}:{port}/lab", delay=open_delay)
    # else:
    #     typer.echo(f"📖 Open http://localhost:{port}/lab manually in your browser")
    
    typer.echo("⏹️  Press Ctrl+C to stop the server")
    typer.echo()
    
    # Change to notebook directory
    os.chdir(sclab_home)
    
    # Check port availability
    if not is_port_available(host, port):
        typer.echo(f"❌ Port {port} is already in use on {host}. Choose a different port with --port.", err=True)
        raise typer.Exit(1)

    # Start JupyterLab
    try:
        subprocess.run([
            sys.executable, "-m", "jupyterlab",
            f"--notebook-dir={sclab_home}",
            # "--no-browser",
            f"--port={port}",
            f"--ServerApp.ip={host}",
            # "--allow-root"
        ], check=True)
    except KeyboardInterrupt:
        typer.echo("\n👋 SCLab-App stopped.")
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Error starting JupyterLab: {e}", err=True)
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("❌ JupyterLab not found. Please ensure it's installed properly.", err=True)
        raise typer.Exit(1)


@app.command()
def dashboard(
    no_browser: Annotated[bool, typer.Option("--no-browser", help="Don't open browser automatically")] = False,
    port: Annotated[int, typer.Option("--port", min=1, max=65535, help="Port for Voila server")] = 8866,
    notebook: Annotated[Optional[Path], typer.Option("--notebook", help="Dashboard notebook path")] = None,
    open_delay: Annotated[int, typer.Option("--open-delay", min=0, max=60, help="Delay (seconds) before opening browser")] = 4,
) -> None:
    """
    📊 Launch SCLab-App Dashboard (Voila interface).
    
    This provides a streamlined dashboard interface for analysis workflows.
    """
    # Set up environment
    sclab_home = ensure_sclab_home()
    dashboard_notebook = notebook or (sclab_home / "dashboard.ipynb")
    
    typer.echo("🧬 Starting SCLab-App Dashboard...")
    typer.echo(f"📓 Dashboard notebook: {dashboard_notebook}")
    typer.echo(f"🌐 Dashboard URL: http://localhost:{port}")
    
    # Check if dashboard notebook exists
    if not dashboard_notebook.exists():
        typer.echo(f"❌ Dashboard notebook not found: {dashboard_notebook}", err=True)
        typer.echo("Please ensure the dashboard notebook exists or run SCLab-App first to create default notebooks.", err=True)
        raise typer.Exit(1)
    
    # if not no_browser:
    #     typer.echo(f"🚀 Opening dashboard in your default browser in {open_delay} seconds...")
    #     open_browser_delayed(f"http://localhost:{port}", delay=open_delay)
    # else:
    #     typer.echo(f"📖 Open http://localhost:{port} manually in your browser")
    
    typer.echo("⏹️  Press Ctrl+C to stop the dashboard")
    typer.echo()
    
    # Change to notebook directory for relative imports
    os.chdir(sclab_home)
    
    # Start Voila
    try:
        subprocess.run([
            sys.executable, "-m", "voila",
            str(dashboard_notebook),
            f"--port={port}",
            "--enable_nbextensions=True",
            # "--no-browser"
        ], check=True)
    except KeyboardInterrupt:
        typer.echo("\n👋 SCLab-App Dashboard stopped.")
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Error starting Voila: {e}", err=True)
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("❌ Voila not found. Please ensure it's installed properly.", err=True)
        raise typer.Exit(1)


@app.command()
def server(
    port: Annotated[int, typer.Option("--port", min=1, max=65535, help="Port for JupyterLab server")] = 8899,
    host: Annotated[str, typer.Option("--host", help="Host/IP to bind the server (e.g., 127.0.0.1 or 0.0.0.0)")] = "127.0.0.1",
    notebook_dir: Annotated[Optional[Path], typer.Option("--notebook-dir", help="Notebook directory")] = None,
    open_delay: Annotated[int, typer.Option("--open-delay", min=0, max=60, help="Delay (seconds) before opening browser")] = 3,
) -> None:
    """
    🖥️  Start SCLab-App server only (no browser).
    
    This starts the JupyterLab server without automatically opening a browser.
    Useful for remote access or when you want to manually navigate to the interface.
    """
    # Set up environment
    sclab_home = notebook_dir or ensure_sclab_home()
    
    typer.echo("🧬 Starting SCLab-App Server...")
    typer.echo(f"📂 Notebook directory: {sclab_home}")
    typer.echo(f"🌐 Server URL: http://localhost:{port}/lab")
    typer.echo("📖 Open the URL above manually in your browser")
    typer.echo("⏹️  Press Ctrl+C to stop the server")
    typer.echo()
    
    # Change to notebook directory
    os.chdir(sclab_home)
    
    # Check port availability
    if not is_port_available(host, port):
        typer.echo(f"❌ Port {port} is already in use on {host}. Choose a different port with --port.", err=True)
        raise typer.Exit(1)

    # Start JupyterLab server only
    try:
        subprocess.run([
            sys.executable, "-m", "jupyterlab",
            f"--notebook-dir={sclab_home}",
            # "--no-browser",
            f"--port={port}",
            f"--ServerApp.ip={host}",
            "--allow-root"
        ], check=True)
    except KeyboardInterrupt:
        typer.echo("\n👋 SCLab-App Server stopped.")
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Error starting JupyterLab: {e}", err=True)
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("❌ JupyterLab not found. Please ensure it's installed properly.", err=True)
        raise typer.Exit(1)


@app.command()
def info() -> None:
    """
    Show SCLab-App information and status.
    """
    sclab_home = get_sclab_home()
    dashboard_exists = check_dashboard_notebook()
    
    typer.echo("🧬 SCLab-App Information")
    typer.echo()
    typer.echo(f"✅ SCLab-App Directory: {sclab_home}")
    typer.echo(f"✅ Dashboard Notebook: {'✅ Found' if dashboard_exists else '❌ Not found'}")
    typer.echo(f"✅ Python: {sys.executable}")
    typer.echo(f"✅ Platform: {platform.system()} {platform.release()}")
    
    # Check if SCLab is available
    try:
        import sclab
        typer.echo(f"🔬 SCLab Version: {sclab.__version__}")
    except ImportError:
        typer.echo("🔬 SCLab: ❌ Not found")
    except AttributeError:
        typer.echo("🔬 SCLab: ✅ Available (version unknown)")
    
    # Check if JupyterLab is available
    try:
        result = subprocess.run([sys.executable, "-m", "jupyterlab", "--version"], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        typer.echo(f"📔 JupyterLab: ✅ {version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        typer.echo("📔 JupyterLab: ❌ Not found")
    
    # Check if Voila is available
    try:
        result = subprocess.run([sys.executable, "-m", "voila", "--version"], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        typer.echo(f"📊 Voila: ✅ {version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        typer.echo("📊 Voila: ❌ Not found")
    
    if sclab_home.exists():
        notebooks = list(sclab_home.glob("*.ipynb"))
        typer.echo(f"📝 Notebooks found: {len(notebooks)}")
        if notebooks:
            for nb in sorted(notebooks)[:5]:  # Show first 5
                typer.echo(f"   • {nb.name}")
            if len(notebooks) > 5:
                typer.echo(f"   ... and {len(notebooks) - 5} more")


@app.command()
def init(
    force: Annotated[bool, typer.Option("--force", help="Overwrite existing notebooks")] = False,
) -> None:
    """
    🎯 Initialize SCLab-App with default notebooks.
    
    This creates the SCLab-App directory and sets up default notebooks
    if they don't already exist.
    """
    sclab_home = ensure_sclab_home()
    
    typer.echo("🎯 Initializing SCLab-App...")
    typer.echo(f"📂 Creating directory: {sclab_home}")
    
    # This would normally call the setup function from the installer
    # For now, we'll create a basic structure
    try:
        # Create subdirectories
        (sclab_home / "data").mkdir(exist_ok=True)
        (sclab_home / "results").mkdir(exist_ok=True)
        (sclab_home / "figures").mkdir(exist_ok=True)
        
        # Create basic dashboard if it doesn't exist or force is True
        dashboard_path = sclab_home / "dashboard.ipynb"
        if not dashboard_path.exists() or force:
            create_basic_dashboard(sclab_home)
            typer.echo(f"📓 Created: {dashboard_path.name}")
        else:
            typer.echo(f"📓 Skipped: {dashboard_path.name} (already exists)")
        
        typer.echo("✅ SCLab-App initialized successfully!")
        typer.echo("🚀 Run 'sclab-app' to start using SCLab-App")
        
    except Exception as e:
        typer.echo(f"❌ Error during initialization: {e}", err=True)
        raise typer.Exit(1)


def create_basic_dashboard(sclab_dir: Path) -> None:
    """Create a basic dashboard notebook."""
    dashboard_path = sclab_dir / "dashboard.ipynb"
    
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


# Legacy entry points for backward compatibility

def main_entry():
    """Entry point for sclab-app command."""
    app()


def dashboard_entry():
    """Entry point for sclab-app-dashboard command."""
    dashboard()


def server_entry():
    """Entry point for sclab-app-server command."""
    server()


if __name__ == "__main__":
    app()
