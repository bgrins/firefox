# nesting-specificity: source companion packaging

Commit the exact **43-file** inventory in [INVENTORY.json](INVENTORY.json), plus this note and that inventory, before the separate native/WPT repair. Inventory SHA-256: `adc34a57f331c115d49eb727da52e0dd2fba246d403e13ba6433b369a47e45c9`. No accepted checker or frozen source is changed by this addendum. Keep this note outside the authenticated proof directory.

## Replay prerequisites

Use css-nesting-specificity-source-package-v1/README.md. The forty-three-file inventory includes the complete original/candidate sources and all 39 replay inputs. It additionally requires 857 pinned third_party/rust files from the checkout. Two cssparser pins are the accepted bad-URL candidate tokenizer/checksum; replay after that repair or with an exact dependency snapshot. The native nesting patch has no corresponding dependency. Historical verify.py and output freezes are intentionally omitted.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 artifacts/css-nesting-specificity-proof-v1/check.py --out NEW_OUTPUT
```

Use fresh output paths and the pinned toolchain/SDK and Lean library prerequisites documented by the companion. These are source packages, not hermetic compiler distributions. This packaging audit inspected closure and source binding; it did not rerun expensive proofs or browsers.

## Repair boundary

Minimal patch: `artifacts/css-nesting-specificity-fix-v1/fix-candidate-v2.patch`; SHA-256 `f1f4f0c6e5673feafce565cb8b853b896d2a8ba69e2c943c4ae6cd19904e1224`. Isolated application and exact reversal at historical HEAD `11482ee213bf63c749b6d205c2c7591d783bdaa8` pass. Every produced native/WPT file matches an accepted source or final browser-input pin. Recheck applicability against the actual preceding commit; do not stage whole combined live files.

## Preserved limitations

Bounded specificity arithmetic and finite crate execution; parser providers/matching/cascade and the separate invalid-parent family remain outside the theorem. No performance rerun is provided by this source package. The authoritative acceptance is `artifacts/css-nesting-specificity-fix-v1/verification-final-v1.json`. This note documents packaging and does not extend that acceptance.
