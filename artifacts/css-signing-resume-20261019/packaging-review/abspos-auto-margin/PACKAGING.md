# abspos-auto-margin: source companion packaging

Commit the exact **23-file** inventory in [INVENTORY.json](INVENTORY.json), plus this note and that inventory, before the separate native/WPT repair. Inventory SHA-256: `b6ddac28f84c39f3ca7cb3d75abffdc1ed0906a58b0a90225ff793a2f1de5a91`. No accepted checker or frozen source is changed by this addendum. Keep this note outside the authenticated proof directory.

## Replay prerequisites

This checker unconditionally authenticates SOURCE-v1.json against repository paths and has no snapshot-only switch. Replay requires the pinned candidate native file(s) and the other pinned live providers. It is valid to commit this tooling before the repair; run the full checker after the exact candidate is available. A combined later worktree can fail the whole-file identity gate. Do not disable the gate or relabel the current checker as pre-fix source-only. The precise live paths/hashes are in packaged SOURCE-v1.json.

```sh
python3 artifacts/css-abspos-auto-margin-proof-v1/check.py --out NEW_OUTPUT
```

Use fresh output paths and the pinned toolchain/SDK and Lean library prerequisites documented by the companion. These are source packages, not hermetic compiler distributions. This packaging audit inspected closure and source binding; it did not rerun expensive proofs or browsers.

## Repair boundary

Minimal patch: `artifacts/css-abspos-auto-margin-fix-v1/fix.patch`; SHA-256 `fb9d633d85b77fcf4fc53df3ff71e6a18f81e39052e0ac31177789fa6b692cfa`. Isolated application and exact reversal at historical HEAD `11482ee213bf63c749b6d205c2c7591d783bdaa8` pass. Every produced native/WPT file matches an accepted source or final browser-input pin. Recheck applicability against the actual preceding commit; do not stage whole combined live files.

## Preserved limitations

Inset-provenance and signed-residual helper model; representability, initially zero automatic margins, anchor/style providers and full reflow remain outside the proved contract. The authoritative acceptance is `artifacts/css-abspos-auto-margin-fix-v1/verification-final-v1.json`. This note documents packaging and does not extend that acceptance.
