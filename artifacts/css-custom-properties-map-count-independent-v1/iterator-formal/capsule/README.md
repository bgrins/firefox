# Iterator proof replay

Authenticate externally supplied `FREEZE.json`, `MANIFEST.json` and `check.py` hashes before executing:

```sh
python3 -I -S artifacts/css-custom-properties-map-iterator-proof-v1/check.py --output /private/tmp/map-iterator-proof-fresh
```

The output path must not exist and must be outside the source capsule. The pinned Lean binary and its Std library installation are external toolchain dependencies. No Rust, browser or Firefox build is run. Copy only the closed capsule to replay at a new path.

Read `REPORT.md` for scope and native/provider premises. The current `getIndex` theorem targets the combined source's live projection; `getIndexRaw` is the historical raw-index contract. Count preservation by insertion/removal/COW is intentionally a separate proof obligation.
