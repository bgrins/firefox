# Zero-tab companion: source-only commit and replay

This guide applies to the source-only package of the frozen v2 companion.
It supplements its retained README, whose first verification command assumes
the full local evidence directory. The source-only commit does not include that
directory's freeze, compiler outputs, or external review logs.

From the repository root, with the declared compiler, SDK, Python and Lean
prerequisites available:

```
PYTHONDONTWRITEBYTECODE=1 python3 artifacts/css-tab-zero-intrinsic-proof-v2/verify.py --source-only
PYTHONDONTWRITEBYTECODE=1 python3 artifacts/css-tab-zero-intrinsic-proof-v2/check.py --out /tmp/zero-tab-replay-new
```

The output directory must not exist. The first command authenticates the packaged
sources; the second compiles and executes the native corpus, Lean models, theorem
audits, semantic mutations and integrity diagnostics. Neither command builds
Gecko or runs a browser. Omit `--live` for an independent checkout or before the
following native repair commit is applied; that optional flag requires the live
Gecko files to match the candidate and provider snapshots.

The preceding tooling commit contains all 31 entries of
`css-tab-zero-intrinsic-proof-v2/SOURCE-ONLY-v1.json`, that manifest itself, and
this guide: 33 files. Preserve their paths. The following standalone fix commit
contains only `layout/generic/nsTextFrame.cpp` and
`testing/web-platform/tests/css/css-text/tab-size/tab-size-zero-intrinsic.html`.

Accepted evidence comprises universal model results under explicit provider and
numeric premises, bounded extracted-native comparisons, and separate paired
browser tests. It does not establish universal C++ refinement, pointer safety,
IEEE arithmetic, font shaping or complete rendering conformance. Saturation
controls are native preservation tests outside the unsaturated Lean bridge.
Positive tabs at zero font size remain a separate defect.
