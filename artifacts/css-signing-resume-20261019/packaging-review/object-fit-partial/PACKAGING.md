# object-fit-partial: source companion packaging

Commit the exact **15-file** inventory in [INVENTORY.json](INVENTORY.json), plus this note and that inventory, before the separate native/WPT repair. Inventory SHA-256: `bfab7a1e64f426d142d11c1ff262ab63cc9dc2e3a27219fb95e04ad19f196e7c`. No accepted checker or frozen source is changed by this addendum. Keep this note outside the authenticated proof directory.

## Replay prerequisites

This checker unconditionally authenticates SOURCE-v1.json against repository paths and has no snapshot-only switch. Replay requires the pinned candidate native file(s) and the other pinned live providers. It is valid to commit this tooling before the repair; run the full checker after the exact candidate is available. A combined later worktree can fail the whole-file identity gate. Do not disable the gate or relabel the current checker as pre-fix source-only. The precise live paths/hashes are in packaged SOURCE-v1.json.

```sh
python3 artifacts/css-object-fit-partial-proof-v1/check.py --out NEW_OUTPUT
```

Use fresh output paths and the pinned toolchain/SDK and Lean library prerequisites documented by the companion. These are source packages, not hermetic compiler distributions. This packaging audit inspected closure and source binding; it did not rerun expensive proofs or browsers.

## Repair boundary

Minimal patch: `artifacts/css-object-fit-partial-fix-v1/fix.patch`; SHA-256 `dca6dc28cbaaae8bc088cdb5443630762fe3cc4172f3c3e42f23c916c593c86e`. Isolated application and exact reversal at historical HEAD `11482ee213bf63c749b6d205c2c7591d783bdaa8` pass. Every produced native/WPT file matches an accepted source or final browser-input pin. Recheck applicability against the actual preceding commit; do not stage whole combined live files.

## Preserved limitations

Partial-natural-dimension object-fit dispatch with provider/numeric premises; no general image sizing/painting theorem. The authoritative acceptance is `artifacts/css-object-fit-partial-fix-v1/verification-final-v1.json`. This note documents packaging and does not extend that acceptance.
