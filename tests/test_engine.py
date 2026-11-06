"""Regression tests against values produced by the published ST calculator script."""
import json
import math
from pathlib import Path

import pytest

from nfc_coil_calculator.coil_engine import CoilSpec, calculate, spiral_points

GOLDEN = json.loads((Path(__file__).parent / "data" / "golden_cases.json").read_text(encoding="utf-8-sig"))


@pytest.mark.parametrize(
    "case",
    GOLDEN,
    ids=[f"{c['input']['turns']}turns-{c['input']['length_mm']:g}x{c['input']['width_mm']:g}" for c in GOLDEN],
)
def test_matches_reference_cases(case):
    result = calculate(CoilSpec(**case["input"]))
    assert result.low_frequency_uh * 1000 == pytest.approx(case["l0_nh"], rel=1e-8)
    assert result.resonance_mhz * 1e6 == pytest.approx(case["srf_hz"], rel=1e-8)
    assert result.equivalent_uh == pytest.approx(case["leq_uh"], rel=1e-8)


@pytest.mark.parametrize(
    "overrides",
    [
        {"turns": 1.5},
        {"turns": 16},
        {"turns": 0},
        {"length_mm": 3},
        {"trace_mm": 0},
        {"spacing_mm": float("nan")},
        {"epsilon_r": 7},
        {"copper_um": -1},
        {"substrate_mm": 0.1},
    ],
)
def test_rejects_invalid_parameters(overrides):
    with pytest.raises(ValueError):
        calculate(CoilSpec(**overrides))


def test_substrate_thickness_does_not_change_the_model():
    assert calculate(CoilSpec(substrate_mm=1)) == calculate(CoilSpec(substrate_mm=2))


def test_default_design_matches_source_default():
    result = calculate(CoilSpec())
    assert result.equivalent_uh == pytest.approx(1.498211799168, rel=1e-11)
    assert result.low_frequency_uh == pytest.approx(1.47219485814284, rel=1e-12)
    assert result.trace_length_mm == pytest.approx(683.4, rel=1e-12)


def test_segment_tables_and_derived_quantities():
    for turns in (1, 2, 3, 8, 15):
        spec = CoilSpec(turns=turns)
        result = calculate(spec)
        assert len(result.segment_lengths_mm) == 4 * turns
        assert len(result.segment_self_nh) == 4 * turns
        assert len(result.segment_mutual_nh) == 4 * turns
        assert result.trace_length_mm == pytest.approx(sum(result.segment_lengths_mm), rel=1e-12)
        assert result.dc_resistance_ohm > 0
        assert result.tuning_pf == pytest.approx(
            1 / ((2 * math.pi * 13.56e6) ** 2 * result.equivalent_uh * 1e-6) * 1e12, rel=1e-12)


def test_spiral_centerline_point_count():
    for turns in (1, 3, 15):
        assert len(spiral_points(CoilSpec(turns=turns))) == 4 * turns + 1


def test_large_design_warns_about_model_accuracy():
    result = calculate(CoilSpec(turns=15))
    assert result.warnings
    assert any("model" in warning.lower() for warning in result.warnings)
