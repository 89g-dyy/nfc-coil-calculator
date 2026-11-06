# Third-party components

## GNU LibreDWG 0.14

Purpose: the standalone `dwgadd.exe` and `dwgwrite.exe` command line tools that build native CAD
objects and write DWG files. The application invokes them as subprocesses and all processing stays on
the local machine.

- Project: https://www.gnu.org/software/libredwg/
- Official code: https://github.com/LibreDWG/libredwg
- Matching version: https://github.com/LibreDWG/libredwg/tree/0.14
- Official release: https://github.com/LibreDWG/libredwg/releases/tag/0.14
- Complete corresponding source: https://github.com/LibreDWG/libredwg/releases/download/0.14/libredwg-0.14.tar.xz
- Source archive SHA256: `62ebb73b984f865960f20ed26619ea5f8789d5e3fd088fa40a2598384da81275`
- Licence: GNU General Public License version 3 or later; the full text ships as
  [`third_party/LIBREDWG-COPYING.txt`](../third_party/LIBREDWG-COPYING.txt).

The converter is used as an unmodified official prebuilt binary. Redistributing it means complying with
the GPL, which includes shipping the licence and the complete corresponding source. The release archive
keeps that material in `sources/`.

LibreDWG is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See its GNU General Public
License for details.

## Python / Tcl / Tk

The one-file executable is produced by PyInstaller and embeds the Python and Tcl/Tk runtimes. Those
runtimes keep their own licences; the relevant texts ship with the release archive.

## PyInstaller

Build tool: https://pyinstaller.org/. GPL v2 or later with a bootloader exception that permits
distributing the generated applications.

## Calculation formulas

The numerical model follows the published script of the ST eDesignSuite NFC Inductance calculator; see
[ALGORITHM.md](ALGORITHM.md). This is an independent implementation, not an ST application, and the
project does not use ST branding for its icon or window.
