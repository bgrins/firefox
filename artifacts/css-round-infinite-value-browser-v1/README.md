# Infinite-value Round observation

Executed the existing `css-round-nonfinite-classification-probe-v1/observe.js`
through Firefox DevTools MCP on system Firefox 158.0. The tool reported the
default system binary; this is not the locally built candidate. The owned blank
tab and probe iframe were removed after observation. No preferences changed.

All 224 snapshots passed syntax support, specified-value admission, repeated
read, literal expectation, font-size, mixed-length and sign calibrations.
There were 53 mismatching snapshots across four already-known categories:

| Case | Mismatches |
|---|---:|
| Contextual infinite value, infinite step | 16 |
| NaN value, infinite step | 16 |
| Infinite value, contextual infinite/NaN step | 16 |
| Contextual finite value, infinite step | 5 |

The current investigation concerns the third row. With an infinite value and
step `infinity * sign(1em - 16px)`, the step becomes negative infinity, NaN,
positive infinity, then negative infinity at font sizes 8, 16, 32, 8 pixels.
Each must yield NaN. Instead, all four strategies serialize the enclosing
opacity expression to `calc(0.75)` and compute 0.75 rather than zero.

The resolved-operand diagnostic also exposes `round(infinity, NaN)` returning
the infinity. These resolved controls are observations, not the expectation
oracle. The expected results follow the CSS Values 4
[argument ranges](https://drafts.csswg.org/css-values-4/#round-infinities) and
[NaN propagation rules](https://drafts.csswg.org/css-values-4/#calc-ieee).

This confirms an existing open lead on the system browser. It is not a new
discovery, a repair count, a local-build result, or new formal coverage.
The existing RoundSpecialKnowledge model already describes why an unknown
step cannot safely be discarded. Candidate validation remains pending.

The MCP result was saved at
`/Users/bgrins/.firefox-devtools-mcp/output/evaluate-script-2026-10-28T23-20-04-277Z.json`
and copied byte-for-byte to `system-observation.json`. `ASSESSMENT.json`
records the observation and source hashes. An earlier attempt to save directly
inside this artifact directory was rejected by the tool's path restriction;
the successful default-location call produced this observation.

## Leaf cases

A second 72-snapshot probe covered both infinity signs, four strategies, and
NaN, relative-length, and fixed-length steps at font sizes 8, 0, 8 pixels.
The fully calibrated result is `system-leaf-detached-observation.json`:
24 NaN-step snapshots and eight relative-step snapshots at zero font size
disagree with the expected result. All fixed-step controls pass. The latter
case uses `round(infinity * 1px, 1em)` (and its negative counterpart): the
coefficient of `1em` is nonzero, but its resolved length is zero.

The first transport result, `system-leaf-observation.json`, lost shared
calibration objects during MCP serialization. Assessment stopped on a missing
field. It is retained as an incomplete transport result, not passing evidence.
The probe was rerun with a JSON round trip around its return value; all 72
snapshots then contained their own calibration fields and passed those checks.
`LEAF-ASSESSMENT.json` refers only to this detached rerun, whose MCP output was
`evaluate-script-2026-10-28T23-21-59-794Z.json`.

The source of this probe is
`artifacts/css-round-infinite-value-review-v1/observation.js`. Candidate design
must account for canonical numeric knowledge, not just syntactic leaves, and
for admission behavior in consumers that require context-free numbers.
