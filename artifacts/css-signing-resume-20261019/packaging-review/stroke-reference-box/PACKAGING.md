# stroke-reference-box: source companion packaging

Commit the exact **15-file** inventory in [INVENTORY.json](INVENTORY.json), plus this note and that inventory, before the separate native/WPT repair. Inventory SHA-256: `cc3cbe232eb6990afc5b6301323d27eb66fdbeffa282d6c9596121a453afa55b`. No accepted checker or frozen source is changed by this addendum. Keep this note outside the authenticated proof directory.

## Replay prerequisites

This checker unconditionally authenticates SOURCE-v1.json against repository paths and has no snapshot-only switch. Replay requires the pinned candidate native file(s) and the other pinned live providers. It is valid to commit this tooling before the repair; run the full checker after the exact candidate is available. A combined later worktree can fail the whole-file identity gate. Do not disable the gate or relabel the current checker as pre-fix source-only. The precise live paths/hashes are in packaged SOURCE-v1.json.

```sh
python3 artifacts/css-stroke-reference-box-proof-v1/check.py --out NEW_OUTPUT
```

Use fresh output paths and the pinned toolchain/SDK and Lean library prerequisites documented by the companion. These are source packages, not hermetic compiler distributions. This packaging audit inspected closure and source binding; it did not rerun expensive proofs or browsers.

## Repair boundary

Minimal patch: `artifacts/css-stroke-reference-box-fix-v1/fix.patch`; SHA-256 `f9304ee1c0e3f7f8e47bee1ca92506a31dafaf3f219e080cd67a704d5f49adfe`. Isolated application and exact reversal at historical HEAD `11482ee213bf63c749b6d205c2c7591d783bdaa8` pass. Every produced native/WPT file matches an accepted source or final browser-input pin. Recheck applicability against the actual preceding commit; do not stage whole combined live files.

## Preserved limitations

CSS reference-box alias and fixed-input cache model; external geometry/provider and invalidation freshness remain premises. The authoritative acceptance is `artifacts/css-stroke-reference-box-fix-v1/verification-final-v1.json`. This note documents packaging and does not extend that acceptance.
