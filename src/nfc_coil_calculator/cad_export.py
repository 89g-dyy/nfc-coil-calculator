"""1:1 millimetre CAD exports, with square-ended copper and mitered corners."""
import math
import json
from pathlib import Path
import re
import subprocess
import tempfile

from .coil_engine import CoilSpec, spiral_points
from .i18n import ValidationError
from .resources import resource_path, tools_dir


def cad_centerline(spec):
    """CAD uses Y up, origin at the lower left of the copper bounding box."""
    return [(x, spec.width_mm - y) for x, y in spiral_points(spec)]


def copper_outline(spec):
    points = cad_centerline(spec)
    half = spec.trace_mm / 2
    directions = []
    for a, b in zip(points, points[1:]):
        length = math.dist(a, b)
        if length <= 1e-12:
            raise ValidationError("error.zero_segment")
        directions.append(((b[0] - a[0]) / length, (b[1] - a[1]) / length))
    sides = []
    for sign in (1, -1):
        side = []
        for i, (x, y) in enumerate(points):
            if i == 0:
                dx, dy = directions[0]
                nx, ny = -dy, dx
            elif i == len(points) - 1:
                dx, dy = directions[-1]
                nx, ny = -dy, dx
            else:
                ax, ay = directions[i - 1]
                bx, by = directions[i]
                dot = ax * bx + ay * by
                if dot < -0.999:
                    raise ValidationError("error.doubling_back")
                nx, ny = (-ay - by) / (1 + dot), (ax + bx) / (1 + dot)
            side.append((x + sign * half * nx, y + sign * half * ny))
        sides.append(side)
    return sides[0] + list(reversed(sides[1]))


def _tags(pairs):
    return "".join(f"{code:3d}\n{value}\n" for code, value in pairs)


def _polyline(points, layer, handle, closed=False):
    pairs = [(0, "LWPOLYLINE"), (5, handle), (330, "17"),
             (100, "AcDbEntity"), (8, layer), (100, "AcDbPolyline"),
             (90, len(points)), (70, int(closed)), (43, "0.0")]
    for x, y in points:
        pairs.extend([(10, f"{x:.10f}"), (20, f"{y:.10f}")])
    return _tags(pairs)


def export_dxf(path, spec: CoilSpec):
    spec.validate()
    text = resource_path("assets/cad_template.dxf").read_text(encoding="ascii")
    entities = _polyline(copper_outline(spec), "COPPER", "35", closed=True)
    entities += _polyline(cad_centerline(spec), "CENTERLINE", "36")
    entities += _polyline([(0, 0), (spec.length_mm, 0),
                           (spec.length_mm, spec.width_mm), (0, spec.width_mm)],
                          "REFERENCE", "37", closed=True)
    # Template is an empty R2000 document with a fixed modelspace record 17.
    pattern = r"(  0\nSECTION\n  2\nENTITIES\n)(.*?)(  0\nENDSEC\n)"
    text, count = re.subn(pattern, lambda m: m[1] + entities + m[3], text, count=1, flags=re.S)
    if count != 1:
        raise ValidationError("error.cad_template")
    Path(path).write_text(text, encoding="ascii", newline="\n")


def dwg_converter():
    path = tools_dir() / "dwgwrite.exe"
    if not path.is_file():
        raise ValidationError("error.converter_missing")
    return path


def export_dwg(path, spec: CoilSpec):
    """Create native entities with LibreDWG, preserving geometry and layer flags.

    Native construction avoids LibreDWG's DXF-import block-record limitations.
    JSON is the library's own intermediate object representation.
    """
    converter = dwg_converter()
    builder = converter.with_name("dwgadd.exe")
    if not builder.is_file():
        raise ValidationError("error.builder_missing")
    spec.validate()
    with tempfile.TemporaryDirectory(prefix="nfc-cad-") as folder:
        root = Path(folder)
        instructions, native, target = root / "coil.add", root / "coil.json", root / "coil.dwg"
        lines = ["version 2000", "HEADER.INSUNITS = 4", "HEADER.MEASUREMENT = 1",
                 "HEADER.EXTMIN = (0 0 0)",
                 f"HEADER.EXTMAX = ({spec.length_mm:.10f} {spec.width_mm:.10f} 0)"]
        for layer in ("COPPER", "CENTERLINE", "REFERENCE"):
            lines.extend([f'layer "{layer}"', 'layer.ltype = "Continuous"'])
            if layer != "COPPER":
                lines.append("layer.flag0 = 2")
        entities = [
            ("COPPER", copper_outline(spec), True),
            ("CENTERLINE", cad_centerline(spec), False),
            ("REFERENCE", [(0, 0), (spec.length_mm, 0),
                            (spec.length_mm, spec.width_mm), (0, spec.width_mm)], True),
        ]
        for layer, points, closed in entities:
            coords = " ".join(f"({x:.10f} {y:.10f})" for x, y in points)
            lines.extend([f"lwpolyline {len(points)} ({coords})", f'lwpolyline.layer = "{layer}"'])
            if closed:
                lines.append("lwpolyline.flag = 512")
        instructions.write_text("\n".join(lines) + "\n", encoding="ascii")

        def run(command):
            return subprocess.run(command, cwd=str(converter.parent), capture_output=True,
                                  timeout=45, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            built = run([str(builder), "--json", "--as", "r2000", "-o", str(native), str(instructions)])
            if not native.is_file():
                raise ValidationError("error.dwg_geometry", detail=built.stderr.decode(errors="replace")[-400:])
            document = json.loads(native.read_text(encoding="utf-8"))
            for obj in document["OBJECTS"]:
                if obj.get("object") == "LAYER" and obj.get("name") in ("COPPER", "CENTERLINE", "REFERENCE"):
                    obj["color"] = {"COPPER": 2, "CENTERLINE": 4, "REFERENCE": 8}[obj["name"]]
            native.write_text(json.dumps(document, ensure_ascii=True), encoding="ascii")
            completed = run([str(converter), "-I", "JSON", "--as", "r2000", "-o", str(target), str(native)])
        except subprocess.TimeoutExpired:
            raise ValidationError("error.dwg_timeout") from None
        except OSError as error:
            raise ValidationError("error.dwg_start", error=error) from error
        if not target.is_file() or target.stat().st_size < 100:
            detail = completed.stderr.decode("utf-8", errors="replace")[-600:]
            raise ValidationError("error.dwg_failed", detail=detail)
        data = target.read_bytes()
        if data[:6] != b"AC1015":
            raise ValidationError("error.dwg_signature")
        # Destination is written only after conversion succeeds, protecting existing files.
        Path(path).write_bytes(data)

