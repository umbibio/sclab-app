import sys
from pathlib import Path


def remove_menu():
    from menuinst.api import remove

    prefix_dir = Path(sys.prefix)

    deleted_files = remove(prefix_dir / "menu" / "sclab-app.json")
    if deleted_files is not None:
        print("Deleted files:")
        for file in deleted_files:
            print("  ", file)
