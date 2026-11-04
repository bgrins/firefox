# Minimal cumulative rollback delivery

fix.patch contains exactly two Rust files and three WPT files. It preserves the exact candidate bytes from the successful current-stack comparison: 74 PASS / 6 FAIL became 80 PASS, preserving all prior passes. Existing rollback controls retained five passes, two known cycle failures, three harness OK outcomes and one passing crashtest. Independent raw and restoration audits passed. See ../css-rollback-current-comparison-v1/README.md.

The selected files apply and reverse against HEAD a6f39620516a4cf76a5dbf5208960adc79068cf1 Git objects in temporary copies. The live sources and untracked probes were not changed. In particular, the selected D fixture has 48 callbacks; the live older D64 probe remains preserved for the separate rule-identity investigation.

Scoped WPT lint and Rustfmt with servo/rustfmt.toml passed. The earlier missing lint.ignore and missing formatter-configuration failures are retained as failed attempts, not passing checks. lint.ignore.input is a supporting linter input, not part of fix.patch or candidate/. Firefox reviewer tooling selected #firefox-style-system-reviewers. commit-message.txt is a prepared local message; no commit has been created.

The patch does not apply to the stale March origin/main merge base because its cascade representation predates the integrated custom-property consumer. Independent review found and checked the retained October pre-project ancestor 976279105b2e78b8666a959eb3f25c9176cefaf8: the same five-file patch applies there cleanly with hunk offsets. See ../css-rollback-landability-review-v1. This is source applicability, not an isolated native build, browser comparison or fresh latest-upstream claim.

The two existing A/B defects and D preservation behavior share required production state. Historical partial repairs regress one another. This delivery keeps the coherent tested unit together; proofs, diagnostics and supporting files belong in a preceding research commit. C rule identity, stronger-rule cycles, and all other project fixes remain outside this patch. Further independent publication review remains explicit; the browser-repair catalogue has not been incremented.
