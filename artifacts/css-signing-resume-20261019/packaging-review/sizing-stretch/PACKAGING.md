# sizing-stretch: source companion packaging

Commit the exact **18-file** inventory in [INVENTORY.json](INVENTORY.json), plus this note and that inventory, before the separate native/WPT repair. Inventory SHA-256: `3c7917cf4070b5cbe7b11af940e9827bbec1f13d6c0189a89f8c9e6f684668c5`. No accepted checker or frozen source is changed by this addendum. Keep this note outside the authenticated proof directory.

## Replay prerequisites

Default replay uses packaged extracted sources. --live is optional and requires exact candidate/caller fragments. The versioned Lean installation is expected under the repository artifacts path.

```sh
python3 artifacts/css-sizing-stretch-proof-v1/check.py NEW_OUTPUT
```

Use fresh output paths and the pinned toolchain/SDK and Lean library prerequisites documented by the companion. These are source packages, not hermetic compiler distributions. This packaging audit inspected closure and source binding; it did not rerun expensive proofs or browsers.

## Repair boundary

Minimal patch: `artifacts/css-sizing-stretch-fix-v1/fix.patch`; SHA-256 `4a1254d702580425c22038183fc64faca4d4a6c9f98648cb84481835fd75f9c0`. Isolated application and exact reversal at historical HEAD `11482ee213bf63c749b6d205c2c7591d783bdaa8` pass. Every produced native/WPT file matches an accepted source or final browser-input pin. Recheck applicability against the actual preceding commit; do not stage whole combined live files.

## Preserved limitations

Finite selection model and extracted bridge; Grid automatic-minimum semantics and full layout remain outside the contract. The authoritative acceptance is `artifacts/css-sizing-stretch-fix-v1/verification.json`. This note documents packaging and does not extend that acceptance.
