# bad-url-recovery: source companion packaging

Commit the exact **229-file** inventory in [INVENTORY.json](INVENTORY.json), plus this note and that inventory, before the separate native/WPT repair. Inventory SHA-256: `4f48806842832f4174945eee2963c5b83ea7f8573d7ab92b2503bce091a4bf9a`. No accepted checker or frozen source is changed by this addendum. Keep this note outside the authenticated proof directory.

## Replay prerequisites

Replay uses packaged tokenizer original/candidate, checksum inputs, macro sources, vendored dependency closure and macro-Cargo.lock. Generated crates, executables and Lean objects are recreated. No live repaired tokenizer is needed.

```sh
python3 artifacts/css-bad-url-recovery-proof-v1/check.py --out NEW_OUTPUT
```

Use fresh output paths and the pinned toolchain/SDK and Lean library prerequisites documented by the companion. These are source packages, not hermetic compiler distributions. This packaging audit inspected closure and source binding; it did not rerun expensive proofs or browsers.

## Repair boundary

Minimal patch: `artifacts/css-bad-url-recovery-fix-v1/fix-candidate-v1.patch`; SHA-256 `48d8285525782d75a6f9f00a64b84d6e797f79d5a99fe1150f1dc239503f8908`. Isolated application and exact reversal at historical HEAD `11482ee213bf63c749b6d205c2c7591d783bdaa8` pass. Every produced native/WPT file matches an accepted source or final browser-input pin. Recheck applicability against the actual preceding commit; do not stage whole combined live files.

## Preserved limitations

Tokenizer recovery model and finite Rust/provider correspondence; not full CSS parsing, rendering or verified compilation. The authoritative acceptance is `artifacts/css-bad-url-recovery-fix-v1/verification-final-v1.json`. This note documents packaging and does not extend that acceptance.
