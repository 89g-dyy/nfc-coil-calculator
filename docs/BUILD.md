# Windows build

The packaged application needs neither a Python installation nor network access. Building it requires
Windows 64-bit, Python 3.10+ with Tcl/Tk and PyInstaller; regenerating the icon additionally needs
Pillow.

```powershell
python -m pip install -e ".[build]"
python scripts/download_libredwg.py
python scripts/create_icon.py      # optional, only when the icon sources change
python scripts/build_exe.py
```

The result is `dist/NFC Coil Calculator.exe`: a PyInstaller one-file, windowed build that embeds
Tcl/Tk, the icon, the CAD template, the DWG converter and its DLLs. On first start it unpacks its
resources into a temporary directory.

## DWG converter

Source: the official LibreDWG 0.14
[Windows 64-bit release](https://github.com/LibreDWG/libredwg/releases/download/0.14/libredwg-0.14-win64.zip).
Download it, extract it, and place `dwgwrite.exe`, `examples/dwgadd.exe` and the required DLLs in
`tools/libredwg/`. A round-trip DWG verification also needs `dwg2dxf.exe` from the same archive.
`python scripts/download_libredwg.py` performs the download, hash check and layout automatically.

SHA256 of the official archive:

```
1ad7e15344d20b3426c3435b078d82fb84b35062815946b2cca9c5fc9810fea8
```

The application calls `dwgadd.exe` in a separate process to build native CAD objects offline and then
`dwgwrite.exe` to emit a binary DWG compatible with AutoCAD 2000 (AC1015). Native object construction
avoids the block-record limitations of the upstream DXF importer.

GNU LibreDWG is licensed under GPL-3.0-or-later. The licence text ships as
`third_party/LIBREDWG-COPYING.txt`; provenance and the way to obtain the complete corresponding source
are described in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). When you pass the packaged
application on, include the licence and source material from the release archive.

## Verification

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m pip install --target verification-output/cad-check --no-deps ezdxf==1.4.3
```

The test suite audits the generated DXF with `ezdxf`, which is a development-only dependency. DWG tests
export a file, convert it back to DXF with `dwg2dxf.exe` and re-run the same checks (units, outline
size, layers); they are skipped when the LibreDWG binaries are not present.

The packaged executable can run the same resource checks without a window and write a report with
sample exports to the given directory:

```powershell
& ".\dist\NFC Coil Calculator.exe" --self-check ".\verification-output\packaged-check"
```

Inspect `self-check.json` for `ok`, `frozen` and the export details. The check covers the default
inductance, the bundled icon, the DXF template and a real DWG file signature.

## Release archive

```powershell
python scripts/download_libredwg.py --source
python scripts/package_release.py
```

`package_release.py` collects the executable, the documentation, the licence texts (including the
LibreDWG corresponding source archive), and writes `SHA256SUMS.txt` plus
`dist/NFC-Coil-Calculator-<version>-Windows.zip`, which is what gets attached to a GitHub release.
