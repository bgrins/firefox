# Signed local checkpoints, 2026-10-27

| Repository | Commit | Contents |
|---|---|---|
| CSS library | `ef6f4dd2ed9499006101ac5299d731109b0361f9` | 64 source files; all 2,153 verification source fingerprints still match the passing report. |
| Firefox | `37e1d4e898c61ad3f0747c8a1cf83fbf3c4483b8` | Animation ownership proposals, regression evidence, failed attempts and remaining obligations. |
| Firefox | `0f0a8a5fb7d5696820350a23613f8989e91069d1` | Steps admission baseline, specification trace, reviewed repair proposal and standalone Lean companion. |

Signatures and exact committed file bodies were verified. The CSS library working changes and prior staging are now committed; only its unrelated `.DS_Store` remains untracked. The recorded integrated proof result is 11,830 audits, 12,424 executable cases and 170 expected-false cases. This signing session checked every recorded source fingerprint; it did not repeat compilation or browser execution.

The [unfinished-work snapshot](../css-unfinished-work-checkpoint-20261027-v1/README.md) preserves all 132 remaining project working files as an exact, reversible patch. This includes 57 modified tracked files and 75 new project files. It excludes unrelated untracked directories and build outputs. The patch was applied to its recorded base in an isolated index, every resulting body was checked, and reversal restored the exact base tree. Native working files remain in place for continued development.

There are still 131 accepted browser fixes, all committed individually. These checkpoints add no accepted bug. Compact borrowing still needs actual compilation and native tests after two Cargo setup failures. The steps proposal still needs lint, compilation and fresh baseline/candidate/restoration browser comparisons. Its separate Lean model has 10 audits, 11 examples and three false controls; it is not yet integrated into the canonical totals and proves no native refinement.

Nothing was pushed or submitted. The source and binary preservation checks are recorded with the signing receipts. Historical epochs retain their original HEAD/index bindings; continued work must use `FINAL-EPOCH.json` from this signing runtime.
