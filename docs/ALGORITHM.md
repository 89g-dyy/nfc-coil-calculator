# Calculation basis and limits

Source: [ST eDesignSuite NFC Inductance](https://eds.st.com/antenna/#/), read on 2026-11-06. The
published main script on that site is
`https://eds.st.com/antenna/main-es2015.3222828bc126a78c3125.js`. This project is an independent Python
implementation of the same formulas and makes no network requests at run time.

## Units

Geometric lengths are in millimetres; the copper thickness is entered in µm and converted to mm.
Segment self-inductance, mutual inductance and their sums use nH, capacitances use F and the
self-resonance scan uses Hz. The interface reports inductance in µH and frequency in MHz.

## Inductance

Every turn is split into four straight segments. For the vertical segmentation, the `t`-th pair of
segments (`t = 0 … 2N−1`) has the lengths:

```
horizontal = outer length − w(t+1) − s·max(0, t−1)
vertical   = outer width − (w+s)t
```

This matches the "segment length" definition used by the source site. It is not the preview
centerline length and must not be used to generate manufacturing data.

Grover segment self-inductance, with `l` the segment length, `w` the trace width and `h` the copper
thickness:

```
Lself[nH] = 0.2·l·[ln(2l/(w+h)) + 0.223(w+h)/l + 0.5]
```

The mutual inductance of parallel segments is computed from the primitive below, where `d` is the
distance between the segments and `a` is a signed axial offset:

```
F(x,d) = x·asinh(x/d) − sqrt(x²+d²)
M[nH] = 0.1·[F(l1+l2+a,d) − F(l1+a,d) − F(l2+a,d) + F(a,d)]
```

Co-directional pairs add and opposite pairs subtract, following the original model; mutual inductance
between perpendicular segments is zero. Each row is summed and then combined with the self-inductance
of that segment. The total mutual term counts both symmetric directions, which is equivalent to
`ΣLself + 2ΣMpair`.

## Parasitic capacitance and frequency correction

For two or more turns the parasitic capacitance is:

```
C[F] = l·[0.12·h/w + 0.09·(1+εr)·log10(1+2w/s+w²/s²)]·10⁻¹³
```

The single-turn case keeps the source site's special form, in which the two bracket terms are
multiplied and the spacing is replaced by `outer width − 2w`. One-turn and two-turn designs use the
source's distributed LC networks; three turns and more use the total impedance of one LC term per
turn. The long two-turn expression lives in `two_turn_network.py` and keeps the original operand order
for comparison.

The scan looks for the first impedance decrease between 25 MHz and 300 MHz: with a 100 kHz step for one
and two turns and 10 kHz otherwise. Multi-turn designs apply the empirical factor
`−0.001·k³+0.0172·k²−0.1031·k+0.9891` with `k=min(N,12)`; three turns are additionally divided by 0.65
and four turns by 0.8. If no minimum is found the source's 300 MHz fallback is kept, the 3/4-turn
special cases are still applied, and the interface warns about the limitation.

```
Leq = Llow / [1 − (13.56 MHz / fmodel)²]
```

The source site derives its accuracy hints from the model frequency: below 30 MHz the error may exceed
15%, from 30 to 35 MHz about 15%, and from 35 to 45 MHz about 10%. The same hints are shown here. They
come from the source rules and are not an independent accuracy measurement of this project.

## Known limits

- Rectangular, single-layer, vertically segmented coils only; circular, stacked, magnetic-material and
  metal-backing models are not implemented.
- The substrate thickness exists in the source input but is never passed to the single-layer formula;
  that behaviour is preserved.
- The self-resonance scan starts at 25 MHz, so it can neither guarantee detection of a real resonance
  below that value nor guarantee that the global first resonance is found. The interface calls the
  result the *model self-resonant frequency*.
- The scan-limit fallback value is not a reliable self-resonance prediction.
- The empirical coefficients and special cases of the source are preserved in order to reproduce its
  numbers; numerical agreement does not validate the physical model itself.
- Lead-in traces, IC packages, vias, pads and manufacturing tolerances are out of scope; the preview
  and the SVG only show the shape.
- DC resistance uses the 20 °C copper resistivity of `1.724×10⁻⁸ Ω·m`; AC resistance and Q are not
  reported, to avoid implying RF accuracy that the model does not have.
- The ideal external parallel tuning capacitance is `1 / [(2π·13.56MHz)²·Leq]`. Coil parasitics are
  already contained in `Leq`, and capacitance contributed by the IC and other external parts must be
  subtracted from the external capacitor.

## Cross-check values

`tests/data/golden_cases.json` was produced by the independent calculation module inside the published
script; no private ST endpoint is called. The cases
cover the single-turn, two-turn and multi-turn branches, the 3/4-turn corrections, the 12-turn
coefficient clamp and the scan fallback. The test suite compares low-frequency inductance, model
self-resonant frequency and the 13.56 MHz equivalent inductance, and also exercises invalid input,
project files and export formats.
