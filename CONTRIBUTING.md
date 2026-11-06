# Contributing

Thanks for taking the time to improve NFC Coil Calculator.

## Getting started

```powershell
git clone https://github.com/89g-dyy/nfc-coil-calculator.git
cd nfc-coil-calculator
python -m pip install -e ".[dev]"
python -m pytest
```

Python 3.10 or newer with Tkinter is required to run the window; the test suite itself needs no
display.

## Project layout

- `src/nfc_coil_calculator/coil_engine.py` – the numerical model. Changes here must keep the reference
  cases in `tests/data/golden_cases.json` passing; if the model intentionally changes, update the
  expected data in the same pull request and explain why.
- `src/nfc_coil_calculator/cad_export.py` – DXF/DWG output. Keep geometry in millimetres at 1:1.
- `src/nfc_coil_calculator/app.py` – Tkinter interface, no calculation logic.
- `docs/` – algorithm notes, build instructions and third-party notices.

## Guidelines

- Keep calculations, file formats and the interface in separate modules.
- Add or update a test for every behaviour change.
- Stay compatible with Python 3.10 and keep the runtime dependency-free; development tools belong in the
  `dev` and `build` extras in `pyproject.toml`.
- Update `CHANGELOG.md` and the relevant documentation when behaviour changes.
- Document any new third-party component in `docs/THIRD_PARTY_NOTICES.md` and check that its licence is
  compatible with MIT.

## Submitting changes

1. Fork the repository and create a topic branch.
2. Make the change, run `python -m pytest`, and keep the diff focused.
3. Open a pull request describing the motivation, the behaviour change and how it was verified.

## Reporting issues

Please include the parameter set (or the saved JSON project), the value you expected, the value you got
and your Python version. Numerical questions are much easier to answer with the exported CSV.
