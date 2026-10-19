# root-rlh-zoom: source companion packaging

Commit the exact **118-file** inventory in [INVENTORY.json](INVENTORY.json), plus this note and that inventory, before the separate native/WPT repair. Inventory SHA-256: `8573a4492031f354c30c2aba1c603fec8be73049586f13eda382f82adb172fae`. No accepted checker or frozen source is changed by this addendum. Keep this note outside the authenticated proof directory.

## Replay prerequisites

Use the exact frozen FREEZE.json hash for FREEZE_SHA256. SOURCE-MANIFEST.json plus itself, FILES.json and FREEZE.json make the 118-file closure. The baseline subdirectory is an authenticated v1 source closure, not generated output. No live repaired length.rs is needed. --source-only without --replay checks integrity only.

```sh
python3 -I -S artifacts/css-root-rlh-zoom-proof-v2/verify.py --source-only --expected-freeze FREEZE_SHA256 --lean ABSOLUTE_LEAN_PATH --replay NEW_OUTPUT
```

Use fresh output paths and the pinned toolchain/SDK and Lean library prerequisites documented by the companion. These are source packages, not hermetic compiler distributions. This packaging audit inspected closure and source binding; it did not rerun expensive proofs or browsers.

## Repair boundary

Minimal patch: `artifacts/css-root-rlh-zoom-fix-v1/fix-candidate-v2.patch`; SHA-256 `fadf1f0641c541279a47e388090e52455c2c62191dd0eb950677e1e9c741f4c6`. Isolated application and exact reversal at historical HEAD `11482ee213bf63c749b6d205c2c7591d783bdaa8` pass. Every produced native/WPT file matches an accepted source or final browser-input pin. Recheck applicability against the actual preceding commit; do not stage whole combined live files.

## Preserved limitations

Unchanged H2 model with dependency-effect supplement; external scheduling/providers, bounded native arithmetic and no universal IEEE/font/layout claim. The authoritative acceptance is `artifacts/css-root-rlh-zoom-fix-v1/ROOT-FORMAL-ACCEPTED-v2.json`. This note documents packaging and does not extend that acceptance.
