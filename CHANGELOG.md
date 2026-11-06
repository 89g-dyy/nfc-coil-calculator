# Changelog

All notable changes to this project are documented in this file. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0]

### Added

- Installable `nfc_coil_calculator` package with a `python -m nfc_coil_calculator` entry point,
  `nfc-coil` command line tool and a packaging self-check (`--self-check DIR`).
- English / Chinese interface with a flag button that switches languages at run time; the initial
  language follows the Windows UI language.
- Pytest suite covering the reference cases, input validation, project files, CSV/SVG exports, DXF
  audits, translations and the window, with an optional DWG round-trip test.
- GitHub Actions continuous integration, issue templates and contribution guide.
- MIT licence.

### Changed

- Repository restructured into an `src/` layout with `pyproject.toml`, `docs/`, `scripts/`.
- Source code, documentation, file names and default file outputs are English.
- Window layout scales with the display DPI, so the interface no longer overflows on 150% or 175%
  scaling.
- CSV headers and project files are English; project files use format `nfc-coil-calculator` version 2
  while files written by earlier versions (`nfc-coil-python` version 1) remain readable.
- Icon generation script cleaned up and extended with the language flag icons.

### Removed

- Prebuilt binaries and vendored archives are no longer stored in the repository; Windows builds are
  published as GitHub releases and the LibreDWG tools are downloaded at build time.

## [1.1.0]

### Added

- Initial packaged Windows release: one-file executable with embedded Tcl/Tk and the offline DWG
  converter, DXF/DWG/CSV/SVG export, project files and the algorithm documentation.
