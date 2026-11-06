"""Text based outputs: JSON projects, CSV result sheets and SVG previews."""
from dataclasses import asdict
from datetime import datetime
import csv
import json
from pathlib import Path

from .coil_engine import CoilResult, CoilSpec, spiral_points
from .i18n import ValidationError, translate
from .params import PARAMETERS

PROJECT_FORMAT = "nfc-coil-calculator"
PROJECT_VERSION = 2

# Project files written by the first public release stay readable.
LEGACY_PROJECT_FORMATS = {"nfc-coil-python"}


def read_project(path):
    if Path(path).stat().st_size > 1024 * 1024:
        raise ValidationError("error.project_large")
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValidationError("error.project_format")
    known_format = data.get("format") in {PROJECT_FORMAT} | LEGACY_PROJECT_FORMATS
    if not known_format or data.get("version") not in (1, PROJECT_VERSION):
        raise ValidationError("error.project_format")
    params = data.get("parameters")
    if not isinstance(params, dict) or set(params) != set(asdict(CoilSpec())):
        raise ValidationError("error.project_parameters")
    spec = CoilSpec(**params)
    spec.validate()
    return spec


def write_project(path, spec):
    payload = {"format": PROJECT_FORMAT, "version": PROJECT_VERSION, "parameters": asdict(spec)}
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def export_csv(path, spec: CoilSpec, result: CoilResult):
    with open(path, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["NFC Coil Calculator", datetime.now().isoformat(timespec="seconds")])
        writer.writerow(["Parameter", "Value", "Unit"])
        for key, title, unit in PARAMETERS:
            writer.writerow([translate("en", title), getattr(spec, key), unit])
        for label, value, unit in [
            ("Equivalent inductance @ 13.56 MHz", result.equivalent_uh, "µH"),
            ("Low-frequency inductance", result.low_frequency_uh, "µH"),
            ("Model self-resonant frequency", result.resonance_mhz, "MHz"),
            ("Model conductor length", result.trace_length_mm, "mm"),
            ("DC resistance estimate @ 20 °C", result.dc_resistance_ohm, "Ω"),
            ("Ideal total tuning capacitance @ 13.56 MHz", result.tuning_pf, "pF"),
        ]:
            writer.writerow([label, value, unit])
        writer.writerow([])
        writer.writerow(["Segment", "Length (mm)", "Self inductance (nH)", "Total mutual (nH)"])
        segments = zip(result.segment_lengths_mm, result.segment_self_nh, result.segment_mutual_nh)
        for index, values in enumerate(segments, 1):
            writer.writerow([f"S{index}", *values])
        for warning in result.warnings:
            writer.writerow(["Warning", warning])


def export_svg(path, spec: CoilSpec):
    pad = max(spec.length_mm, spec.width_mm) * 0.09
    points = " ".join(f"{x:.6f},{y:.6f}" for x, y in spiral_points(spec))
    Path(path).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="800" '
        f'viewBox="{-pad} {-pad} {spec.length_mm + 2*pad} {spec.width_mm + 2*pad}">\n'
        f'<title>NFC rectangular spiral: {spec.turns:g} turns, {spec.length_mm:g} × {spec.width_mm:g} mm</title>\n'
        '<desc>Visual preview only. Not a PCB manufacturing file; terminals and routing require engineering.</desc>\n'
        f'<polyline points="{points}" fill="none" stroke="#b77c23" stroke-width="{spec.trace_mm}" '
        'stroke-linejoin="miter" stroke-linecap="butt"/>\n</svg>\n', encoding="utf-8")
