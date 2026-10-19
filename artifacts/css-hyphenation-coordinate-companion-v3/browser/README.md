# Hyphenation measurement offset repair

A soft hyphen discovered in a later measurement chunk must update cached automatic break candidates. The old guard compares an absolute word boundary to a buffer-relative length; the repair compares two absolute positions.

- Paired browser run: two failing cases become eight passing cases, with six baseline controls preserved.
- Twenty existing tests retain nineteen passes and one expected failure.
- Patch: `fix-coordinate-v1.patch`, one comparison in gfxTextRun.cpp plus one WPT. It excludes the independent signed-ligature repair and applies/reverses at the base and HEAD.
- Root independently compiled nine Lean coordinate/refill theorems. Full native consumer composition and machine/font premises remain explicit.

Read `ROOT-NATIVE-WPT-v1.json`, `NATIVE-BINDING-v1.json`, `STANDALONE-COORDINATE-v1.json`, and `root-lean-v1/RESULT.json` for the receipts and boundaries. The configured signer still blocks committing; the index and HEAD are preserved.
