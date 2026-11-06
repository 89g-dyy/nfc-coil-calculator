"""Reproducible one-file Windows build: python scripts/build_exe.py."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "nfc_coil_calculator"
TOOLS = ROOT / "tools" / "libredwg"
APP_NAME = "NFC Coil Calculator"


def main():
    converter = TOOLS / "dwgwrite.exe"
    builder = TOOLS / "dwgadd.exe"
    if not converter.is_file() or not builder.is_file():
        raise SystemExit("Missing tools/libredwg binaries; run "
                         "python scripts/download_libredwg.py first (see docs/BUILD.md).")
    args = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
            "--name", APP_NAME, "--icon", str(PACKAGE / "assets" / "icon.ico"),
            "--add-data", f"{PACKAGE / 'assets'}{os.pathsep}assets",
            "--add-binary", f"{converter}{os.pathsep}tools/libredwg",
            "--add-binary", f"{builder}{os.pathsep}tools/libredwg",
            "--version-file", str(ROOT / "scripts" / "version_info.txt"),
            "--paths", str(ROOT / "src"),
            "--distpath", str(ROOT / "dist"), "--workpath", str(ROOT / "build"),
            str(ROOT / "scripts" / "entry.py")]
    for dll in converter.parent.glob("*.dll"):
        args.extend(["--add-binary", f"{dll}{os.pathsep}tools/libredwg"])
    subprocess.run(args, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
