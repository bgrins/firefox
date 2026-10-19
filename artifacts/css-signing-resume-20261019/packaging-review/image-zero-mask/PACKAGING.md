# image-zero-mask: source companion packaging

Commit the exact **24-file** inventory in [INVENTORY.json](INVENTORY.json), plus this note and that inventory, before the separate native/WPT repair. Inventory SHA-256: `6fba6d4a2e5c3905500543abd0d1479735917992a33f8901ae9d3ae359fa9b77`. No accepted checker or frozen source is changed by this addendum. Keep this note outside the authenticated proof directory.

## Replay prerequisites

Use the packaged SOURCE-PACKAGE-v2.md and check.py entrypoint. Historical verify.py, freeze and preparation-output receipt checking are intentionally outside this compact source companion. All REPLAY-INPUTS-v1.json computational inputs are included. Omit --skip-mutations for accepted full replay.

```sh
python3 artifacts/css-image-empty-fill-proof-v1/check.py --out NEW_OUTPUT
```

Use fresh output paths and the pinned toolchain/SDK and Lean library prerequisites documented by the companion. These are source packages, not hermetic compiler distributions. This packaging audit inspected closure and source binding; it did not rerun expensive proofs or browsers.

## Repair boundary

Minimal patch: `artifacts/css-image-zero-mask-fix-v1/fix-candidate-v2.patch`; SHA-256 `1a03e1ace14ba854da79b9c852859a1e4e75226518c2f239bb4a6e4340c2a40e`. Isolated application and exact reversal at historical HEAD `11482ee213bf63c749b6d205c2c7591d783bdaa8` pass. Every produced native/WPT file matches an accepted source or final browser-input pin. Recheck applicability against the actual preceding commit; do not stage whole combined live files.

## Preserved limitations

Scoped prepared-empty-fill mask composition and lifetime controls; no general painting/raster/provider theorem. The authoritative acceptance is `artifacts/css-image-zero-mask-fix-v1/verification-final-v1.json`. This note documents packaging and does not extend that acceptance.
