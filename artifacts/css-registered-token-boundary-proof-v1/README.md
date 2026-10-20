# Replay

Authenticate the externally supplied SHA256 of FREEZE.json, MANIFEST.json and check.py before execution. Then copy only manifest-listed files plus those two metadata files into a fresh directory and run:

```
python3 -I -S /absolute/capsule/check.py --output /absolute/fresh/external/output
```

The output path is resolved and must be outside the capsule and nonexistent. Python standard library, pinned installed Lean and its pinned library inventory, pinned installed rustc, Rust stdlib/system linker/runtime are trusted external dependencies. No network, Cargo downloads, Gecko build or browser is used. Ordinary cssparser byte dispatch is compiled; optional macro/serde/malloc features are not.

Read REPORT.md for the exact universal theorem and the remaining balanced-serialization/parser correspondence premises. This is a producer companion awaiting independent review, not a full CSS serialization verification.
