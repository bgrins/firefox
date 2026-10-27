# Existing order regressions

The raw repair proposal requires preserving “existing order regressions.” This is the opposite-resolution-order pair already in `attr-cycle.html`, also identified explicitly by the used-fallback proposal's `REGRESSION-ROSTER.json`. Both helper calls and all surrounding setup are unchanged by the raw repair.

One case defines `--x: attr(data-foo)` and resolves `--y: attr(data-foo type(*))`, with data-foo containing `attr(data-bar, 11) var(--x, 3)` and data-bar containing `var(--x)`. Its expected result is the two literal strings `"var(--x)" "attr(data-bar, 11) var(--x, 3)"`. The other swaps --x and --y to exercise the opposite resolution order and expects the correspondingly renamed two strings. Their observed harness identities are `CSS Values and Units Test: attr 26` and `CSS Values and Units Test: attr 27`.

`ORDER-GATE.json` binds both exact unchanged helper calls and observed identities to the historical and corrected fixture hashes. The corrected attr-cycle page is one of the two targets in both phases. The candidate therefore must pass both order assertions as part of the full 73-target gate. Neither is one of the three explicitly corrected raw-nested oracles.

The unchanged used-fallback fixture additionally contains `missing-bare-mutual` and `missing-bare-mutual-reordered`, testing declaration-order variants of a used raw-fallback property cycle. They remain in the 329-assertion regression signature comparison. Unexpected baseline failures remain visible and require investigation before acceptance.

No additional order fixture is needed to satisfy this named existing-regression gate. This mapping does not claim exhaustive verification of native resolution ordering. The proposal's acceptance wording, native demand-resolver gates, and prohibition on hidden expectation changes remain in force.
