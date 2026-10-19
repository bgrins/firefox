# Replay

Authenticate the externally supplied `FREEZE.json`, `MANIFEST.json` and `check.py` hashes before executing:

```sh
python3 -I -S artifacts/css-custom-properties-map-composition-proof-v1/check.py --output /private/tmp/map-composition-fresh
```

The output directory must be fresh and outside the source root. The exact Lean executable and library identities are inherited from the iterator capsule. Python and standard Lean runtime/compiler semantics remain trusted. The checker is isolated, authenticates all inputs and dependency seals before output creation, and never reads live Firefox source.

Read REPORT and SOURCE-MAPPING for the exact remaining native/caller admissions. Copy manifest-listed source files plus the manifest/seal to relocate; preserve imported predecessor bytes. No Rust/browser/Firefox build is run.
