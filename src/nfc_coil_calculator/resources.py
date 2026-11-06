"""Locate read-only resource files in a source checkout and in frozen builds."""
from pathlib import Path
import os
import sys

PACKAGE_DIR = Path(__file__).resolve().parent


def _frozen_base():
    return Path(getattr(sys, "_MEIPASS", PACKAGE_DIR))


def resource_path(relative):
    """Resolve a bundled read-only file, for example ``assets/icon.ico``."""
    return _frozen_base() / relative


def tools_dir():
    """Directory holding the LibreDWG command line tools.

    Search order: the ``NFC_COIL_LIBREDWG_DIR`` environment variable, the frozen
    bundle, then ``tools/libredwg`` in the repository root.
    """
    override = os.environ.get("NFC_COIL_LIBREDWG_DIR")
    if override:
        return Path(override)
    if getattr(sys, "frozen", False):
        return _frozen_base() / "tools" / "libredwg"
    for parent in PACKAGE_DIR.parents:
        candidate = parent / "tools" / "libredwg"
        if candidate.is_dir():
            return candidate
    return PACKAGE_DIR.parents[2] / "tools" / "libredwg"
