# Public parser history admission

This source-only component joins immutable byte input and position-keyed cache transitions to the previously accepted tracking-epoch model. It also models annotation writes separately from token replay.

Authenticate `FREEZE.json`, `MANIFEST.json` and `check.py` against the independently supplied hashes before execution. Copy exactly the manifest-listed files plus those two seal files to a clean directory, then run:

```
python3 -I -S /path/to/capsule/check.py --run --output /path/to/new-output
```

The output must be outside the source capsule. Pinned Lean and Rust binaries are external tools identified in `TOOLCHAIN.json`; no shared installation is changed. All native compilation uses the copied complete cssparser and dependency sources. No browser, Mach build, native Firefox edit or Git operation is performed.

Read `REPORT.md` and `SOURCE-ADMISSION.md` for the exact projection and remaining premises. This is not whole-parser or whole-tokenizer verification. The preserved late-enable, query/re-enable and annotation histories are counterexamples to broader claims.
