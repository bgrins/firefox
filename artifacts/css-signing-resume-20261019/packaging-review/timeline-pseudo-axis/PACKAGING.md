# timeline-pseudo-axis: source companion packaging

Commit the exact **42-file** inventory in [INVENTORY.json](INVENTORY.json), plus this note and that inventory, before the separate native/WPT repair. Inventory SHA-256: `39c24826ee3ba671d39fde800fb20df4a47d7422b3f7f49c02edd74df65460c9`. No accepted checker or frozen source is changed by this addendum. Keep this note outside the authenticated proof directory.

## Replay prerequisites

Use the pinned interpreter/toolchain from TOOLCHAINS-v1.json. SOURCE-MANIFEST-v1.json supplies all 40 source inputs; the manifest and preceding guide complete the 42-file inventory. --live is optional. The guide’s --clean additionally uses the macOS sandbox and a discoverable checkout; --replay operates on the retained source closure.

```sh
python3 -I -S artifacts/css-timeline-pseudo-axis-proof-v1/verify.py --expected-manifest 239760bee07c24b078c67a42531595e7c4ac1e6fd85b3ce42b88875ccc99d155 --replay NEW_OUTPUT
```

Use fresh output paths and the pinned toolchain/SDK and Lean library prerequisites documented by the companion. These are source packages, not hermetic compiler distributions. This packaging audit inspected closure and source binding; it did not rerun expensive proofs or browsers.

## Repair boundary

Minimal patch: `artifacts/css-timeline-pseudo-axis-fix-v1/fix-candidate-v2.patch`; SHA-256 `71668b8bc901757f77ed90e7a8f5d2822720bf190298822ec3141a4ab2877f04`. Isolated application and exact reversal at historical HEAD `11482ee213bf63c749b6d205c2c7591d783bdaa8` pass. Every produced native/WPT file matches an accepted source or final browser-input pin. Recheck applicability against the actual preceding commit; do not stage whole combined live files.

## Preserved limitations

Scoped pseudo-timeline axis/provider correspondence; recreation-opacity and independent scheduler/lifetime behavior remain separate. The authoritative acceptance is `artifacts/css-timeline-pseudo-axis-fix-v1/verification-final-v1.json`. This note documents packaging and does not extend that acceptance.
