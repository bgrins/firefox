# animation-composite: source companion packaging

Commit the exact **90-file** inventory in [INVENTORY.json](INVENTORY.json), plus this note and that inventory, before the separate native/WPT repair. Inventory SHA-256: `ef1fefb5f80992b7f5c43bbb8185201f4ec2f9473574272ce7ec6689bdd43532`. No accepted checker or frozen source is changed by this addendum. Keep this note outside the authenticated proof directory.

## Replay prerequisites

The ninety-file inventory contains 88 authenticated inputs plus INPUTS.json and FREEZE.json. The checker copies the exact authenticated source closure before running. Historical development/replay outputs are omitted and not imported. No live repaired KeyframeEffect.cpp is needed.

```sh
python3 -I -S -B artifacts/css-animation-composite-proof-v3/check.py --manifest-sha 9dc4204e44dd25c536cf32661cac24d9756997782d31b8ecc62a373635f907d9 --output NEW_OUTPUT
```

Use fresh output paths and the pinned toolchain/SDK and Lean library prerequisites documented by the companion. These are source packages, not hermetic compiler distributions. This packaging audit inspected closure and source binding; it did not rerun expensive proofs or browsers.

## Repair boundary

Minimal patch: `artifacts/css-animation-composite-fix-v1/fix-candidate-v1.patch`; SHA-256 `da678f21283f2bb9d0f3ec620fe550adff78cbb7ec1ef0705873c0731d4a8b1a`. Isolated application and exact reversal at historical HEAD `11482ee213bf63c749b6d205c2c7591d783bdaa8` pass. Every produced native/WPT file matches an accepted source or final browser-input pin. Recheck applicability against the actual preceding commit; do not stage whole combined live files.

## Preserved limitations

Ordinary-WAAPI model under explicit readiness/provider/scheduler premises; finite native correspondence, no verified C++/IEEE or full browser scheduling theorem. The authoritative acceptance is `artifacts/css-animation-composite-fix-v1/ROOT-FORMAL-ACCEPTED-v3.json`. This note documents packaging and does not extend that acceptance.
