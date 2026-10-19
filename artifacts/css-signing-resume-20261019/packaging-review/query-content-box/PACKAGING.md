# query-content-box: source companion packaging

Commit the exact **25-file** inventory in [INVENTORY.json](INVENTORY.json), plus this note and that inventory, before the separate native/WPT repair. Inventory SHA-256: `8a1863f336b54becf14d780b1448163c60d7b8d32079b83c87e80916cbde41be`. No accepted checker or frozen source is changed by this addendum. Keep this note outside the authenticated proof directory.

## Replay prerequisites

This checker unconditionally authenticates SOURCE-v1.json against repository paths and has no snapshot-only switch. Replay requires the pinned candidate native file(s) and the other pinned live providers. It is valid to commit this tooling before the repair; run the full checker after the exact candidate is available. A combined later worktree can fail the whole-file identity gate. Do not disable the gate or relabel the current checker as pre-fix source-only. The precise live paths/hashes are in packaged SOURCE-v1.json.

```sh
python3 artifacts/css-query-content-box-proof-v1/check.py --out NEW_OUTPUT
```

Use fresh output paths and the pinned toolchain/SDK and Lean library prerequisites documented by the companion. These are source packages, not hermetic compiler distributions. This packaging audit inspected closure and source binding; it did not rerun expensive proofs or browsers.

## Repair boundary

Minimal patch: `artifacts/css-query-content-box-fix-v1/fix.patch`; SHA-256 `8a7855e12617af972ba92efbf0149c1b939b37140585081e8c9646151f5e5064`. Isolated application and exact reversal at historical HEAD `11482ee213bf63c749b6d205c2c7591d783bdaa8` pass. Every produced native/WPT file matches an accepted source or final browser-input pin. Recheck applicability against the actual preceding commit; do not stage whole combined live files.

## Preserved limitations

Fixed-type content-size/cache-observable model under layout and provider premises; no full container-query scheduling/layout theorem. The authoritative acceptance is `artifacts/css-query-content-box-fix-v1/verification-final-v1.json`. This note documents packaging and does not extend that acceptance.
