# Font threshold source companion

Commit the 61 authenticated source and bootstrap paths listed in
css-font-threshold-fix-v1/verification-final-v1.json, plus this guide, before the
separate two-file Gecko/WPT repair. Historical output and binaries are excluded.

The producer README describes its handoff state. Root and independent review
subsequently accepted the B-only native/WPT and scoped formal gates; the separate
A priority repair and its original/A-only/combined browser matrix remain pending.

From the repository root, use a fresh output directory:

```sh
python3 -I -B artifacts/css-font-threshold-proof-v1/check.py \
  --manifest-sha256 854cc622b2c0c7f4ad15b552c0f14df8ac43eea6e69713a68dc4e49a76723495 \
  --source-only-replay --out /tmp/font-threshold-replay
```

Authenticate check.py separately before executing it: SHA-256
`eb11a6ac16055425664e918ae289ce530f86b58d708f114fdb4ae0ec846180d4`.
The checker authenticates all 59 computational inputs before helper imports.
The pinned Lean/clang toolchain and SDK are external dependencies; this package
is source-only, not hermetic. No live Gecko source or historical receipts are
needed for replay.

The 24 Lean theorems cover the approved same-sign interval and italic-positive
fallback model. Bounded native execution supplies a separate bridge through the
complete affected consumers. Neither establishes full CSS font matching, C++
refinement, arbitrary provider traces, parser correctness or rendering correctness.
