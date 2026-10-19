# svg-empty-mask: source companion packaging

Commit the exact **24-file** inventory in [INVENTORY.json](INVENTORY.json), plus this note and that inventory, before the separate native/WPT repair. Inventory SHA-256: `2bce58813b1c9d91f7954d4d2017e5268ad919be2e41aef60b12c5be734aec1f`. No accepted checker or frozen source is changed by this addendum. Keep this note outside the authenticated proof directory.

## Replay prerequisites

Replay authenticates REPLAY-INPUTS-v2.json and packaged complete native sources. No live repaired Gecko source is needed. Keep the rejected-v1 finding and v2 scope inputs as listed; omit --skip-mutations for accepted full replay.

```sh
python3 artifacts/css-empty-mask-composition-proof-v2/check.py --out NEW_OUTPUT
```

Use fresh output paths and the pinned toolchain/SDK and Lean library prerequisites documented by the companion. These are source packages, not hermetic compiler distributions. This packaging audit inspected closure and source binding; it did not rerun expensive proofs or browsers.

## Repair boundary

Minimal patch: `artifacts/css-svg-empty-mask-fix-v1/fix-candidate-v2.patch`; SHA-256 `63d30905e4e7ca91fb272769091a8f8a0fa7ce33f062f2ab2cb7c5c06b100386`. Isolated application and exact reversal at historical HEAD `11482ee213bf63c749b6d205c2c7591d783bdaa8` pass. Every produced native/WPT file matches an accepted source or final browser-input pin. Recheck applicability against the actual preceding commit; do not stage whole combined live files.

## Preserved limitations

Scoped empty-region mask composition and admitted providers; no general rendering or numerical/raster theorem. The authoritative acceptance is `artifacts/css-svg-empty-mask-fix-v1/verification-final-v1.json`. This note documents packaging and does not extend that acceptance.
