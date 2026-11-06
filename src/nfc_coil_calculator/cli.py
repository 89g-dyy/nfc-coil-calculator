"""Command line entry point: open the window or run a packaging self check."""
import argparse
import json
import math
from pathlib import Path
import sys

from . import __version__
from .cad_export import export_dwg, export_dxf
from .coil_engine import CoilSpec, calculate
from .resources import resource_path

# Reference value produced by the default parameters.
DEFAULT_EQUIVALENT_UH = 1.498211799168263


def self_check(destination):
    """Exercise the bundled resources and DWG converter without an installed Python."""
    folder = Path(destination)
    folder.mkdir(parents=True, exist_ok=True)
    report = {"ok": False, "frozen": bool(getattr(sys, "frozen", False))}
    try:
        spec = CoilSpec()
        result = calculate(spec)
        assert math.isclose(result.equivalent_uh, DEFAULT_EQUIVALENT_UH, rel_tol=1e-10)
        export_dxf(folder / "coil.dxf", spec)
        export_dwg(folder / "coil.dwg", spec)
        assert resource_path("assets/icon.ico").is_file()
        assert (folder / "coil.dwg").read_bytes()[:6] == b"AC1015"
        report.update(ok=True, equivalent_uh=result.equivalent_uh, dwg_version="AC1015",
                      dxf_bytes=(folder / "coil.dxf").stat().st_size,
                      dwg_bytes=(folder / "coil.dwg").stat().st_size)
    except Exception as error:
        report["error"] = repr(error)
    (folder / "self-check.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                            encoding="utf-8")
    return 0 if report["ok"] else 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="nfc-coil-calculator",
        description="Offline calculator for rectangular 13.56 MHz NFC PCB spiral coils.")
    parser.add_argument("--self-check", metavar="DIR",
                        help="write a resource and CAD export report to DIR, then exit")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)
    if args.self_check:
        return self_check(args.self_check)
    from .app import main as run_window
    return run_window()


if __name__ == "__main__":
    sys.exit(main())
