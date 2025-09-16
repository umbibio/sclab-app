#!/usr/bin/env python3
"""
SCLab-App post-installation setup script.
Creates cross-platform launchers and sets up default notebooks.
"""

import sys
import platform
import shutil
import subprocess
import importlib.resources as pkg_resources
from pathlib import Path
from PIL import Image


def create_png_icons(source_image, output_dir, base_name):
    """Create PNG icons in multiple sizes for Linux."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    sizes = [16, 24, 32, 48, 64, 96, 128, 256]

    with Image.open(source_image) as img:
        for size in sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            output_path = output_dir / f"{base_name}_{size}x{size}.png"
            resized.save(output_path)
            print(f"Created PNG: {output_path}")

        # Main icon (128x128 is common default)
        main_icon = img.resize((128, 128), Image.Resampling.LANCZOS)
        main_path = output_dir / f"{base_name}.png"
        main_icon.save(main_path)
        print(f"Created main PNG: {main_path}")

    return main_path


def create_ico_icon(source_image, output_path):
    """Create Windows ICO file with multiple sizes."""
    output_path = Path(output_path)

    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

    with Image.open(source_image) as img:
        # Create list of resized images
        icon_images = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized)

        # Save as ICO with all sizes
        icon_images[0].save(
            output_path, format="ICO", sizes=sizes, append_images=icon_images[1:]
        )
        print(f"Created ICO: {output_path}")

    return output_path


def create_icns_icon(source_image, output_path):
    """Create macOS ICNS file (requires pillow-heif or iconutil on macOS)."""
    output_path = Path(output_path)

    # Try using pillow to create ICNS directly
    try:
        with Image.open(source_image) as img:
            # Create iconset directory structure
            iconset_dir = output_path.with_suffix(".iconset")
            iconset_dir.mkdir(exist_ok=True)

            # Standard macOS icon sizes
            sizes = [
                (16, 16, "icon_16x16.png"),
                (32, 32, "icon_16x16@2x.png"),
                (32, 32, "icon_32x32.png"),
                (64, 64, "icon_32x32@2x.png"),
                (128, 128, "icon_128x128.png"),
                (256, 256, "icon_128x128@2x.png"),
                (256, 256, "icon_256x256.png"),
                (512, 512, "icon_256x256@2x.png"),
                (512, 512, "icon_512x512.png"),
                (1024, 1024, "icon_512x512@2x.png"),
            ]

            for width, height, filename in sizes:
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
                resized.save(iconset_dir / filename)

            # Try to use iconutil to create ICNS (macOS only)
            try:
                subprocess.run(
                    [
                        "iconutil",
                        "-c",
                        "icns",
                        str(iconset_dir),
                        "-o",
                        str(output_path),
                    ],
                    check=True,
                )
                print(f"Created ICNS: {output_path}")

                # Cleanup iconset directory
                import shutil

                shutil.rmtree(iconset_dir)
                return output_path

            except subprocess.CalledProcessError:
                print(
                    f"Warning: iconutil failed, keeping iconset directory: {iconset_dir}"
                )

    except Exception as e:
        print(f"Error creating ICNS: {e}")
        print("Manual ICNS creation may be required")

    return None


def create_all_icons():
    """Create all icon formats for all app variants."""

    prefix_dir = Path(sys.prefix)
    menu_dir = prefix_dir / "menu"
    source_image = menu_dir / "sclab-logo.png"

    logo_variants = [
        ("sclab-app", "SCLab-App Main"),
    ]

    print(f"Creating icons from source: {source_image}")

    for base_name, description in logo_variants:
        print(f"\nCreating icons for {description}...")

        if sys.platform == "linux":
            # PNG for Linux
            create_png_icons(source_image, menu_dir, base_name)

        elif sys.platform == "win32":
            # ICO for Windows
            create_ico_icon(source_image, menu_dir / f"{base_name}.ico")

        elif sys.platform == "darwin":
            # ICNS for macOS
            create_icns_icon(source_image, menu_dir / f"{base_name}.icns")

        else:
            print(f"Error: Unsupported platform: {sys.platform}")
            sys.exit(1)


def install_menu():
    from menuinst.api import install

    prefix_dir = Path(sys.prefix)

    create_all_icons()
    created_files = install(prefix_dir / "menu" / "sclab-app.json")
    if created_files is not None:
        print("Created files:")
        for file in created_files:
            print("  ", file)


def install_python_packages():
    """Install pip-only dependencies and the bundled sclab-app wheel.

    Looks for the wheel under $PREFIX/share/sclab-app/wheels/ created by Constructor's extra_files.
    Also installs pip-only dependencies that are not reliably available on conda across platforms.
    """
    wheel_dir = Path(sys.prefix) / "share" / "sclab-app" / "wheels"
    # Candidate locations where constructor may have placed the wheel
    script_dir = Path(__file__).resolve().parent
    wheel_search_dirs = [
        wheel_dir,
        Path(sys.prefix) / "dist",
        Path(sys.prefix),
        script_dir,  # e.g., scripts/ alongside this file
        script_dir.parent,  # repo-style layout fallback
    ]

    packages = [
        # Pip-only or better served from PyPI for consistency
        "scikit-misc>=0.5.1",
        "scrublet>=0.2.3",
        "typer>=0.9.0",
        "pyranges>=0.1.4",
    ]

    print("Installing Python packages with pip (post-install)...")
    # Install our application wheel first if present
    wheel_path = None
    for d in wheel_search_dirs:
        try:
            if d.exists():
                candidates = sorted(d.glob("sclab_app-*.whl"))
                if candidates:
                    wheel_path = candidates[0]
                    break
        except Exception:
            # Ignore any permission or glob errors and continue to next dir
            pass

    if wheel_path is not None:
        try:
            print(f"Installing bundled wheel from: {wheel_path}")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--no-input", str(wheel_path)],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install wheel {wheel_path.name}: {e}")
    else:
        print(
            "No bundled sclab-app wheel found in expected locations; proceeding to install pip-only deps."
        )

    # Install additional pip packages
    try:
        print(f"Installing pip packages: {', '.join(packages)}")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--no-input", *packages],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to install some pip packages: {e}")


def copy_packaged_resources():
    """Copy packaged resources (assets, notebooks) from the installed wheel.

    We include resources under `sclab_app/resources/` in the wheel. This copies
    those into the end-user's installation prefix and Documents folder.
    """
    try:
        # Copy assets into $PREFIX/share/sclab-app/assets
        target_assets = Path(sys.prefix) / "share" / "sclab-app" / "assets"
        target_assets.mkdir(parents=True, exist_ok=True)
        try:
            with pkg_resources.as_file(
                pkg_resources.files("sclab_app").joinpath("resources/assets")
            ) as assets_dir:
                if assets_dir.exists():
                    print(f"Copying packaged assets to: {target_assets}")
                    shutil.copytree(assets_dir, target_assets, dirs_exist_ok=True)
        except FileNotFoundError:
            pass

        # Copy notebooks into ~/Documents/SCLab-App if they don't exist yet
        docs_home = Path.home() / "Documents" / "SCLab-App"
        docs_home.mkdir(parents=True, exist_ok=True)
        try:
            with pkg_resources.as_file(
                pkg_resources.files("sclab_app").joinpath("resources/notebooks")
            ) as nb_dir:
                if nb_dir.exists():
                    print(
                        f"Seeding notebooks from packaged resources into: {docs_home}"
                    )
                    for item in nb_dir.iterdir():
                        dest = docs_home / item.name
                        if item.is_dir():
                            shutil.copytree(item, dest, dirs_exist_ok=True)
                        else:
                            if not dest.exists():
                                shutil.copy2(item, dest)
        except FileNotFoundError:
            pass
    except Exception as e:
        print(f"Warning: Failed to copy packaged resources: {e}")


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
                        "4. Explore your results with interactive visualizations",
                    ],
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
                        "app",
                    ],
                },
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                },
                "language_info": {"name": "python", "version": "3.12.0"},
            },
            "nbformat": 4,
            "nbformat_minor": 4,
        }

        import json

        with open(dashboard_path, "w") as f:
            json.dump(basic_dashboard, f, indent=2)


def main():
    """Main setup function."""
    print("Setting up SCLab-App...")
    print(f"Python executable: {sys.executable}")
    print(f"Installation prefix: {sys.prefix}")
    print(f"Platform: {platform.system()}")
    print()

    try:
        # Install Python packages (wheel + pip deps)
        install_python_packages()

        # Copy packaged resources (assets, notebooks)
        copy_packaged_resources()

        # Create launcher scripts
        install_menu()

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
