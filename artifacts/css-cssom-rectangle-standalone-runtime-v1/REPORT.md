# Standalone CSSOM rectangle variant experiment

The experiment completed and restored source/build, HEAD and index. Root ran the builds and browser tests; the assigned independent reviewer reconstructed raw outcomes and sealed this capsule at root's request. No raw log or test/source input was changed during sealing.

| Actual variant | New eight tests | Existing 66 subtests | File outcomes |
|---|---|---|---|
| Baseline | 4 PASS / 4 FAIL | 64 PASS / 2 expected FAIL | 22 OK / 1 PASS |
| DOMRect only | 6 PASS / 2 FAIL | unchanged | unchanged |
| Integer translation only | 6 PASS / 2 FAIL | unchanged | unchanged |
| Both | 8 PASS | unchanged | unchanged |

Each single patch fixes its own two large-box cases. The identity-transformed exponent-boundary box remains on the matrix path and distinguishes DOMRect publication. The ordinary untransformed large box distinguishes integer translation. Horizontal/vertical and small-box controls calibrate the host, a small endpoint marker, supported size and both bounding/client rectangle APIs. These tests preserve their author's assertions; only titles and descriptive assertion messages were adjusted before execution.

The 21 existing test files cover existing CSSOM geometry, SVG foreignObject, 3D context behavior, iframe hit testing, ResizeObserver and IntersectionObserver. Their outcomes are unchanged. The two expected failures concern rotated SVG text/Range bounds and trailing surrogate indexing; the retained metadata marks them expected. The one reftest passes. Exit 1 in single-patch runs reflects the other new repair's two still-failing cases, not unexpected existing regressions.

All four runs have 86 unchanged before/after pins. The only source differences are the designated DOMRect.cpp and/or nsLayoutUtils.cpp changes, plus the rebuilt Firefox executable and XUL. Complete actual source snapshots and raw structured events are retained. All three candidate builds and restoration build exit 0; WPT lint exits 0. Default clang-format-check exit 0 was not warning-free: format-warning-details-v2.log retains the single helper-signature wrapping warning. A later formatted/performance run is separate evidence.

This uses the pinned shared project build, with prior local changes. It demonstrates separately executable witnesses and no regression in the selected finite matrix; it is not isolated upstream validation, all-platform coverage, a performance conclusion, or closure of the original safe-origin F1–F12 proof. The earlier combined 28-test matrix includes fractional-host cases that require both fixes and records a DOM-only numeric error becoming larger without any newly failing status. Its diagnostic ResizeObserver contentRect values can change independently of unchanged size arrays.

COMPARISON.json derives its rows from RUN.json/raw.json; the separately sealed independent review reconstructs the raw events, exact source/test bindings and closed rosters. The final native candidate still needs its exact formatting transfer and other root acceptance gates. No new fix count or landing decision is made by this runtime capsule.
