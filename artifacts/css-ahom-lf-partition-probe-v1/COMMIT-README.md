# Supplementary complex-script line breaking

The native commit contains the vendored ICU handler correction, its Cargo
checksum, and `complex-prefix-lf-partition.html`. The preceding companion
contains the source replay package and the evidence supporting this narrow
backport. The mechanism was already structurally corrected by ICU4X PR 8144.

Start with `ROOT-SCOPED-ACCEPTANCE-v1.json` and
`../css-ahom-acceptance-packaging-review-v1/REPORT.md`.
That report distinguishes universal mathematical lemmas, concrete kernel
witnesses, bounded native execution, and browser observations.

The complete offline source replay instructions are in
`../css-ahom-acceptance-packaging-review-v1/SOURCE-COMMIT.md`. The original
capsule is committed without generated output. To rerun the packaging audit's
`check.py`, first copy the manifest-selected candidate capsule to this
directory's `root-full-replay-v2/` and perform that complete replay there.
The audit checks the regenerated native/kernel results against the frozen
capsule, as well as the retained browser receipts and source snapshots.

`paired-original-v1` and `paired-candidate-v1` are the valid browser pair.
Their binaries are identified by hashes, not included. These are combined-tree
macOS runs, not clean-base, release-browser, or cross-platform validation.
The earlier stale-binary experiment is not acceptance evidence.

Original language/caller/consumer proof obligations remain open. In particular,
raw LF partition equality remains refuted even after this repair. This commit
does not change that contract or claim complete formal verification of CSS.
