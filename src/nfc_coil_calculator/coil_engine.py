"""Offline NFC rectangular spiral model. All geometry is in mm unless named.

The numerical conventions match the ST eDesignSuite calculator retrieved
2026-11-06. See docs/ALGORITHM.md for scope, units and the original model's limits.
"""
from dataclasses import asdict, dataclass
import math

from .i18n import Message, ValidationError
from .two_turn_network import two_turn_impedance


@dataclass(frozen=True)
class CoilSpec:
    turns: int = 3
    length_mm: float = 75.0
    width_mm: float = 45.0
    trace_mm: float = 0.6
    spacing_mm: float = 0.6
    copper_um: float = 35.0
    substrate_mm: float = 1.0
    epsilon_r: float = 4.6

    @property
    def minimum_dimension(self):
        return math.ceil(100 * (2 * self.turns * (self.trace_mm + self.spacing_mm)
                                - self.spacing_mm)) / 100

    def validate(self):
        for key, value in asdict(self).items():
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValidationError("error.field_finite", field=key)
        if int(self.turns) != self.turns or not 1 <= self.turns <= 15:
            raise ValidationError("error.turns")
        if not 0.15 <= self.trace_mm <= 6:
            raise ValidationError("error.trace")
        if not 0.15 <= self.spacing_mm <= 2:
            raise ValidationError("error.spacing")
        if self.copper_um <= 0.1 or self.substrate_mm <= 0.1:
            raise ValidationError("error.thickness")
        if not 2 <= self.epsilon_r <= 6:
            raise ValidationError("error.permittivity")
        if min(self.length_mm, self.width_mm) <= self.minimum_dimension:
            raise ValidationError("error.minimum_dimension", minimum=self.minimum_dimension)
        if max(self.length_mm, self.width_mm, self.copper_um) > 1e6:
            raise ValidationError("error.numeric_range")


@dataclass(frozen=True)
class CoilResult:
    equivalent_uh: float
    low_frequency_uh: float
    resonance_mhz: float
    trace_length_mm: float
    dc_resistance_ohm: float
    tuning_pf: float
    segment_lengths_mm: tuple
    segment_self_nh: tuple
    segment_mutual_nh: tuple
    warnings: tuple


def spiral_points(p):
    """Continuous centerline used by the original site's preview; no closed rings."""
    pitch = p.trace_mm + p.spacing_mm
    x, y = -(p.spacing_mm + p.trace_mm / 2), p.trace_mm / 2
    length, width = p.length_mm + p.spacing_mm, p.width_mm - p.trace_mm
    points = []
    for turn in range(int(p.turns)):
        points.extend([(x + (pitch if turn == 0 else 0), y),
                       (x + length, y), (x + length, y + width),
                       (x + pitch, y + width)])
        if turn == p.turns - 1:
            points.append((x + pitch, y + pitch))
        x, y = x + pitch, y + pitch
        length, width = length - 2 * pitch, width - 2 * pitch
    return points


def calculate(p: CoilSpec) -> CoilResult:
    p.validate()
    turns = int(p.turns)
    count = 4 * turns
    w, gap, thick = p.trace_mm, p.spacing_mm, p.copper_um / 1000
    pitch = w + gap
    fseg = lambda dimension, a, b: dimension - w * a - gap * b
    lengths = []
    for t in range(2 * turns):
        lengths.extend([fseg(p.length_mm, t + 1, max(0, t - 1)),
                        fseg(p.width_mm, t, t)])
    distances = [[0.0] * count for _ in range(count)]
    offsets = [[0.0] * count for _ in range(count)]

    def distance(a, b, value):
        distances[a - 1][b - 1] = distances[b - 1][a - 1] = value

    def offset(a, b, value):
        offsets[a - 1][b - 1] = value

    for t in range(1, turns + 1):
        for e in range(t, turns + 1):
            a, b, delta = 4 * (t - 1), 4 * (e - 1), e - t
            if e == t:
                distance(a + 1, b + 3, w + fseg(p.width_mm, 2 * e, 2 * (e - 1)))
                distance(a + 2, b + 4, w + fseg(p.length_mm, 2 * e, 2 * (e - 1)))
            else:
                for left, right in [(1, 1), (2, 2), (3, 3), (4, 4)]:
                    distance(a + left, b + right, delta * pitch)
                for left, right in [(1, 3), (3, 1)]:
                    distance(a + left, b + right, w + fseg(p.width_mm, e + t, e + t - 2))
                for left, right in [(2, 4), (4, 2)]:
                    distance(a + left, b + right, w + fseg(p.length_mm, e + t, e + t - 2))
            if t == 1:
                offset(a + 1, b + 3, fseg(0, -(delta + 1), -delta))
                if e > t:
                    offset(a + 1, b + 1, fseg(0, -delta, -(delta - 1)))
                    offset(a + 3, b + 1, (delta - 1) * pitch)
                    offset(a + 4, b + 2, (delta - 1) * pitch)
                offset(a + 2, b + 2, delta * pitch)
                offset(a + 2, b + 4, (delta + 1) * pitch)
                offset(a + 3, b + 3, delta * pitch)
                offset(a + 4, b + 4, delta * pitch)
            else:
                if e > t:
                    offset(a + 3, b + 3, delta * pitch)
                    offset(a + 4, b + 4, delta * pitch)
                    offset(a + 3, b + 1, (delta - 1) * pitch)
                    offset(a + 2, b + 4, (delta + 1) * pitch)
                    offset(a + 4, b + 2, (delta - 1) * pitch)
                else:
                    offset(a + 2, b + 4, (delta + 1) * pitch)
                    offset(a + 4, b + 2, delta * pitch)
                offset(a + 1, b + 1, delta * pitch)
                offset(a + 1, b + 3, (delta + 1) * pitch)
                offset(a + 2, b + 2, delta * pitch)
    for t in range(count):
        for e in range(t + 2, count, 2):
            value = offsets[t][e] - lengths[t]
            offsets[t][e] = offsets[e][t] = value

    self_nh = [0.2 * length * (math.log(2 * length / (w + thick))
                              + 0.223 * (w + thick) / length + 0.5) for length in lengths]
    mutual_nh = []
    for t in range(count):
        row = 0.0
        for e in range(count):
            d, a = distances[t][e], offsets[t][e]
            if d != 0 and a != 0:
                def primitive(x):
                    return x * math.asinh(x / d) - math.hypot(x, d)
                b, c = lengths[t], lengths[e]
                mutual = 0.1 * (primitive(b + c + a) - primitive(b + a)
                                - primitive(c + a) + primitive(a))
                row += mutual if (e - t) % 4 == 0 else -mutual
        mutual_nh.append(row)
    segment_h = [(a + b) * 1e-9 for a, b in zip(self_nh, mutual_nh)]
    total_nh = sum(self_nh) + sum(mutual_nh)

    def capacitance(length, spacing=gap, single=False):
        param = math.log10(1 + 2 * w / spacing + w * w / (spacing * spacing))
        term1 = 0.12 * thick / w
        term2 = 0.09 * (1 + p.epsilon_r) * param
        return length * (term1 * term2 if single else term1 + term2) * 1e-13

    if turns == 1:
        caps = [capacitance((lengths[i] + lengths[i + 2]) / 2,
                            p.width_mm - 2 * w, True) for i in range(2)]

        def impedance(freq):
            omega = 2 * math.pi * freq
            a, b, c, d = [omega * value for value in segment_h]
            r = -1 / (omega * caps[0])
            i = r + b + c
            left = -1 / (omega * caps[1]) + b * c / i
            right = d + r * c / i
            return abs(a + left * right / (left + right) + r * b / i)
    elif turns == 2:
        caps = [capacitance((lengths[i] + lengths[i + 4]) / 2) for i in range(4)]

        def impedance(freq):
            return two_turn_impedance(segment_h, caps, 2 * math.pi * freq)
    else:
        turn_h = [sum(segment_h[i:i + 4]) for i in range(0, count, 4)]
        turn_lengths = [sum(lengths[i:i + 4]) for i in range(0, count, 4)]
        caps = [0.0] + [capacitance((turn_lengths[i - 1] + turn_lengths[i]) / 2)
                        for i in range(1, turns)]

        def impedance(freq):
            omega = 2 * math.pi * freq
            return abs(sum(omega * induct / (1 - induct * cap * omega * omega)
                           for induct, cap in zip(turn_h, caps)))

    step = 100000 if turns <= 2 else 10000
    resonance = 300e6
    previous = impedance(25e6)
    scan_found = False
    for freq in range(25000000, 300000001, step):
        try:
            current = impedance(freq + step)
        except ZeroDivisionError:
            current = math.inf
        if previous > current:
            k = min(turns, 12)
            factor = 1 if turns <= 2 else -0.001 * k**3 + 0.0172 * k**2 - 0.1031 * k + 0.9891
            resonance = freq * factor
            scan_found = True
            break
        previous = current
    if turns == 3:
        resonance /= 0.65
    elif turns == 4:
        resonance /= 0.8
    equivalent = total_nh / (1 - (13.56e6 / resonance)**2) / 1000
    if not math.isfinite(equivalent) or equivalent <= 0:
        raise ValidationError("error.no_inductance")
    warnings = []
    if resonance < 30e6:
        warnings.append(Message("warning.accuracy_over_15"))
    elif resonance < 35e6:
        warnings.append(Message("warning.accuracy_15"))
    elif resonance < 45e6:
        warnings.append(Message("warning.accuracy_10"))
    if not scan_found:
        warnings.append(Message("warning.scan_fallback"))
    if sum(self_nh) <= 0 or any(v <= 0 for v in segment_h):
        warnings.append(Message("warning.negative_segments"))
    length = sum(lengths)
    resistance = 1.724e-8 * (length / 1000) / (w / 1000 * p.copper_um * 1e-6)
    tuning = 1 / ((2 * math.pi * 13.56e6)**2 * equivalent * 1e-6) * 1e12
    return CoilResult(equivalent, total_nh / 1000, resonance / 1e6, length,
                      resistance, tuning, tuple(lengths), tuple(self_nh),
                      tuple(mutual_nh), tuple(warnings))
