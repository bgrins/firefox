# Standalone integration accepted

Signed standalone commit `898fb45815c115362093116d81c09715ba94fcab` installs
39 files from the exact reviewed overlay. Its signature was verified. The
existing default `CssSemantics` target remains separate from opt-in
`CssDerivation`; no CSS feature coverage was added by this integration.

Root ran the clean source-only replay and then the installed checker. Both
passed 143 audits, nine controls and 13 rows for each of three actual-file
runners. Every installed source hash and axiom inventory matches the replay.
The actual canonical default build and opt-in build passed. Static coverage
registration passed for 11,923 declarations. The existing core source, coverage
and checker files and the preexisting `.DS_Store` retain their hashes.

This gate does not repeat the full historical runtime suite. The default build
uses existing valid build artifacts as well as the modules it rebuilt; the
derivation checker separately builds its inputs from source in temporary trees.
Those temporary trees were removed. The canonical package's active `.lake`
cache remains available for subsequent work.

`ROOT-INTEGRATION.json` records the delivered hashes and test receipts;
`COMMIT.json` records the signed commit and exact file inventory. Independent
review is in `../css-first-order-library-integration-review-20261110-v1`.
The preceding source-only experiments retain the explicit JSON-text, general
document construction, shared primitive meaning and prose mapping boundaries.
