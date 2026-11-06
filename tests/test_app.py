"""Smoke tests for the Tkinter window; skipped when no display is available."""
import tkinter as tk

import pytest

from nfc_coil_calculator.i18n import LANGUAGES, translate


def _display_available():
    try:
        root = tk.Tk()
    except tk.TclError:
        return False
    root.destroy()
    return True


pytestmark = pytest.mark.skipif(not _display_available(), reason="no Tk display available")


def test_language_switch_updates_the_window():
    from nfc_coil_calculator.app import CoilApp

    app = CoilApp()
    try:
        app.update()
        first = app.language
        assert app.title() == translate(first, "app.title")
        app.toggle_language()
        app.update()
        second = app.language
        assert second != first
        assert set((first, second)) == set(LANGUAGES)
        assert app.title() == translate(second, "app.title")
        assert app.scale >= 1.0
    finally:
        app.close()
