# scroll-fixed-anchor: source companion packaging

Commit the exact **39-file** inventory in [INVENTORY.json](INVENTORY.json), plus this note and that inventory, before the separate native/WPT repair. Inventory SHA-256: `8f5562c3fb501c65ff8444e72ab110cf3e72b763840ee621a2234a65411f985f`. No accepted checker or frozen source is changed by this addendum. Keep this note outside the authenticated proof directory.

## Replay prerequisites

SOURCE-ONLY-v1.json and packaged native snapshots support replay without the live repair. --live is an optional additional gate. The default check.py calls the included extension_check.py automatically. Do not use --skip-mutations: it also skips the required interpreter extension.

```sh
python3 artifacts/css-scroll-fixed-anchor-proof-v2/verify.py --source-only
python3 artifacts/css-scroll-fixed-anchor-proof-v2/check.py --out NEW_OUTPUT
```

Use fresh output paths and the pinned toolchain/SDK and Lean library prerequisites documented by the companion. These are source packages, not hermetic compiler distributions. This packaging audit inspected closure and source binding; it did not rerun expensive proofs or browsers.

## Repair boundary

Minimal patch: `artifacts/css-scroll-fixed-anchor-fix-v1/fix-candidate-v1.patch`; SHA-256 `3939af4d7f5886dfbf563d15a461697bd7ab03ae52ab53875f0cef97f0a739d7`. Isolated application and exact reversal at historical HEAD `11482ee213bf63c749b6d205c2c7591d783bdaa8` pass. Every produced native/WPT file matches an accepted source or final browser-input pin. Recheck applicability against the actual preceding commit; do not stage whole combined live files.

## Preserved limitations

Fixed-anchor collection with provider/traversal premises; no full scrolling/layout or scheduling theorem. The authoritative acceptance is `artifacts/css-scroll-fixed-anchor-fix-v1/verification-final-v2.json`. This note documents packaging and does not extend that acceptance.
