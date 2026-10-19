# Replay

Authenticate the externally supplied FREEZE.json, MANIFEST.json and check.py hashes before running code. Run:

```
python3 -I -S /absolute/capsule/check.py --output /absolute/fresh/external/output
```

The checker uses the pinned installed Lean executable and library listed in TOOLCHAIN.json and TOOLCHAIN-LIBRARY.json. All model, source and provenance inputs are retained; no live source tree, Git, browser, Firefox build or network is needed. Manifest-only relocation is supported. Outputs are generated outside the source capsule and may be removed after retaining logs and CHECK.json.

Read SOURCE-MAPPING.md before instantiating the theorems on native data. Input identity is not verified translation. The checker rejects optimized/nonisolated Python, altered or extra/missing inputs, symlinks, duplicate JSON names and output paths resolving inside the source capsule. External authentication is still required against a self-consistent replacement of the capsule itself.
