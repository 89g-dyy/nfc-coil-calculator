"""Project, CSV, SVG and CAD export checks that need no GUI."""
from dataclasses import asdict
import json
import math
from pathlib import Path

import pytest

from nfc_coil_calculator.cad_export import cad_centerline, copper_outline, export_dxf, export_dwg
from nfc_coil_calculator.coil_engine import CoilSpec, calculate
from nfc_coil_calculator.exports import export_csv, export_svg, read_project, write_project
from nfc_coil_calculator.resources import tools_dir


def test_project_round_trip(tmp_path):
    spec = CoilSpec(turns=5, length_mm=40, width_mm=25, trace_mm=0.8, spacing_mm=0.4)
    path = tmp_path / "coil.json"
    write_project(path, spec)
    assert read_project(path) == spec
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["format"] == "nfc-coil-calculator" and payload["version"] == 2


def test_legacy_project_file_is_still_readable(tmp_path):
    path = tmp_path / "legacy.json"
    payload = {"format": "nfc-coil-python", "version": 1, "parameters": asdict(CoilSpec())}
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert read_project(path) == CoilSpec()


@pytest.mark.parametrize(
    "payload",
    [
        "[]",
        '{"format": "other", "version": 2, "parameters": {}}',
        '{"format": "nfc-coil-calculator", "version": 9, "parameters": {}}',
        '{"format": "nfc-coil-calculator", "version": 2, "parameters": {"turns": 3}}',
    ],
)
def test_malformed_project_is_rejected(tmp_path, payload):
    path = tmp_path / "broken.json"
    path.write_text(payload, encoding="utf-8")
    with pytest.raises(ValueError):
        read_project(path)


def test_csv_export_contains_parameters_results_and_segments(tmp_path):
    spec = CoilSpec()
    path = tmp_path / "results.csv"
    export_csv(path, spec, calculate(spec))
    text = path.read_text(encoding="utf-8-sig")
    assert "NFC Coil Calculator" in text
    assert "Equivalent inductance @ 13.56 MHz" in text
    assert "S12" in text
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")


def test_svg_export_keeps_one_polyline_per_centerline(tmp_path):
    import xml.etree.ElementTree as ET

    spec = CoilSpec(turns=4)
    path = tmp_path / "preview.svg"
    export_svg(path, spec)
    polyline = ET.parse(path).find("{http://www.w3.org/2000/svg}polyline")
    assert len(polyline.attrib["points"].split()) == 4 * spec.turns + 1
    assert float(polyline.attrib["stroke-width"]) == spec.trace_mm


def test_copper_outline_area_matches_centerline_length():
    for turns in (1, 2, 3, 8, 15):
        spec = CoilSpec(turns=turns)
        points = copper_outline(spec)
        area = abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1]))) / 2
        line = cad_centerline(spec)
        expected = spec.trace_mm * sum(math.dist(a, b) for a, b in zip(line, line[1:]))
        assert area == pytest.approx(expected, rel=1e-8)


def test_dxf_export_writes_millimetre_layers(tmp_path):
    spec = CoilSpec()
    path = tmp_path / "coil.dxf"
    export_dxf(path, spec)
    text = path.read_text(encoding="ascii")
    assert text.count("LWPOLYLINE") == 3
    for layer in ("COPPER", "CENTERLINE", "REFERENCE"):
        assert layer in text


def test_dxf_export_survives_independent_audit(tmp_path):
    ezdxf = pytest.importorskip("ezdxf", reason="ezdxf is an optional development dependency")
    from ezdxf import bbox

    spec = CoilSpec(turns=3, length_mm=28, width_mm=20, trace_mm=1.1, spacing_mm=0.2)
    path = tmp_path / "coil.dxf"
    export_dxf(path, spec)
    doc = ezdxf.readfile(path)
    audit = doc.audit()
    assert not audit.has_errors and not audit.has_fixes
    assert doc.units == 4
    assert len(list(doc.modelspace())) == 3
    copper = list(doc.modelspace().query('LWPOLYLINE[layer=="COPPER"]'))
    assert len(copper) == 1 and copper[0].closed
    assert doc.layers.get("CENTERLINE").is_off()
    assert doc.layers.get("REFERENCE").is_off()
    bounds = bbox.extents(copper)
    assert bounds.extmin.x == pytest.approx(0, abs=1e-7)
    assert bounds.extmin.y == pytest.approx(0, abs=1e-7)
    assert bounds.extmax.x == pytest.approx(spec.length_mm, abs=1e-7)
    assert bounds.extmax.y == pytest.approx(spec.width_mm, abs=1e-7)


def test_dwg_export_returns_ac1015(tmp_path):
    if not (tools_dir() / "dwgwrite.exe").is_file():
        pytest.skip("LibreDWG tools are not downloaded; run scripts/download_libredwg.py")
    spec = CoilSpec(turns=2)
    path = tmp_path / "coil.dwg"
    export_dwg(path, spec)
    assert path.read_bytes()[:6] == b"AC1015"
