# Replay

Authenticate MANIFEST.json against the externally supplied freeze, then run:

```
python3 -I -S /absolute/path/to/check.py --output NEW_DIRECTORY
```

Requirements: Python 3, `/usr/bin/patch`, and the exact Lean toolchain recorded in TOOLCHAIN.json. Lean's standard library, kernel/runtime and compiler are external trusted tools. The checker hashes the executable. No Firefox/native build, browser, network or Git is used.

For source-only relocation copy precisely MANIFEST.json's paths plus MANIFEST.json and FREEZE.json. No generated files belong in this capsule. Keep replay receipts outside it. Read SCOPE.md before treating any result as native correspondence.
