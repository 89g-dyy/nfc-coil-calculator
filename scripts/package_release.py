"""Collect the executable, notices and licenses into a portable release archive."""
from pathlib import Path
import hashlib
import re
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
VERSION = re.search(r'__version__ = "([^"]+)"',
                    (ROOT / "src" / "nfc_coil_calculator" / "__init__.py").read_text(encoding="utf-8")).group(1)
EXE = DIST / "NFC Coil Calculator.exe"
RELEASE = DIST / f"NFC-Coil-Calculator-{VERSION}-Windows.zip"

licenses = DIST / "licenses"
licenses.mkdir(parents=True, exist_ok=True)
for source, name in [
    (ROOT / "third_party" / "LIBREDWG-COPYING.txt", "LibreDWG-GPL-3.0.txt"),
    (Path(sys.base_prefix) / "LICENSE.txt", "Python-LICENSE.txt"),
    (Path(sys.base_prefix) / "tcl/tk8.6/license.terms", "Tk-license.terms"),
    (Path(sys.base_prefix) / "tcl/tcl8.6/license.terms", "Tcl-license.terms"),
]:
    if source.exists():
        shutil.copy2(source, licenses / name)

for name in ("README.md", "LICENSE", "CHANGELOG.md"):
    shutil.copy2(ROOT / name, DIST / name)
for name in ("ALGORITHM.md", "BUILD.md", "THIRD_PARTY_NOTICES.md"):
    shutil.copy2(ROOT / "docs" / name, DIST / name)

(DIST / "QUICKSTART.txt").write_text(
    f"NFC Coil Calculator {VERSION}\n\n"
    "Double-click \"NFC Coil Calculator.exe\" to start. No Python installation is needed and the app "
    "runs fully offline.\n"
    "Antenna length and width are the copper outer edges; spacing is the edge-to-edge gap.\n"
    "DXF and DWG export at 1:1 in millimetres. COPPER is the closed copper outline; CENTERLINE and "
    "REFERENCE start hidden.\n"
    "DWG is AutoCAD 2000 binary format. Exports contain no pads, vias or terminals.\n"
    "See README.md for details, BUILD.md for the build steps and licenses/ for third-party notices.\n",
    encoding="utf-8-sig")

if not EXE.is_file():
    raise SystemExit("Build the executable first: python scripts/build_exe.py")
official_source = DIST / "sources" / "libredwg-0.14.tar.xz"
if not official_source.exists():
    raise SystemExit("Download the corresponding LibreDWG source first: "
                     "python scripts/download_libredwg.py --source")

(DIST / "SHA256SUMS.txt").write_text(
    "\n".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(DIST).as_posix()}"
              for p in [EXE, official_source, DIST / "README.md"]) + "\n", encoding="utf-8")

with zipfile.ZipFile(RELEASE, "w", zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(DIST.rglob("*")):
        if file.is_file() and file != RELEASE:
            archive.write(file, file.relative_to(DIST))
print(f"EXE: {EXE} ({EXE.stat().st_size / 1024 / 1024:.1f} MB)")
print(f"Release: {RELEASE} ({RELEASE.stat().st_size / 1024 / 1024:.1f} MB)")
