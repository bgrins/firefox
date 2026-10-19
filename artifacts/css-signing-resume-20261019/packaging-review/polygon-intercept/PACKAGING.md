# polygon-intercept: source companion packaging

Commit the exact **17-file** inventory in [INVENTORY.json](INVENTORY.json), plus this note and that inventory, before the separate native/WPT repair. Inventory SHA-256: `f2dc2b86b4b78ece3bcc608e0877cbb2682f2eb859a0d88d4a8a906e45f996fd`. No accepted checker or frozen source is changed by this addendum. Keep this note outside the authenticated proof directory.

## Replay prerequisites

This checker unconditionally authenticates SOURCE-v1.json against repository paths and has no snapshot-only switch. Replay requires the pinned candidate native file(s) and the other pinned live providers. It is valid to commit this tooling before the repair; run the full checker after the exact candidate is available. A combined later worktree can fail the whole-file identity gate. Do not disable the gate or relabel the current checker as pre-fix source-only. The checker also directly reads native_path and helper_path from its BINDING record. The precise live paths/hashes are in packaged SOURCE-v1.json.

```sh
python3 artifacts/css-polygon-intercept-proof-v1/check.py --out NEW_OUTPUT
```

Use fresh output paths and the pinned toolchain/SDK and Lean library prerequisites documented by the companion. These are source packages, not hermetic compiler distributions. This packaging audit inspected closure and source binding; it did not rerun expensive proofs or browsers.

## Repair boundary

Minimal patch: `artifacts/css-polygon-intercept-fix-v1/fix.patch`; SHA-256 `ada0dab4601333e6cbdc32a9e4e38aadc34845317d1a172ae915df0a344b8bd9`. Isolated application and exact reversal at historical HEAD `11482ee213bf63c749b6d205c2c7591d783bdaa8` pass. Every produced native/WPT file matches an accepted source or final browser-input pin. Recheck applicability against the actual preceding commit; do not stage whole combined live files.

## Preserved limitations

Bounded wide-interpolation arithmetic under admitted coordinates; no proof of every upstream geometry path or rasterization. The authoritative acceptance is `artifacts/css-polygon-intercept-fix-v1/verification-final-v1.json`. This note documents packaging and does not extend that acceptance.
