# Native number differential protocol

A reviewable source proposal connecting the completed JSON lexical bridge to the existing cssparser numeric harness. The corpus preserves the old 84 captures and adds bounded reset histories, UTF-8 start offsets and 254–257-byte boundaries. [PROTOCOL.md](PROTOCOL.md) gives the exact scope and pending gates.

**No native build or execution has occurred.** The inherited direct-rustc build recipe is prepared; a default-feature Cargo recipe and lock remain a required follow-up. This capsule makes no production-feature-equivalence or native-refinement claim.

Static validation only:

```sh
python3 -B artifacts/css-number-native-differential-protocol-20261110-v1/check.py
```

`STATIC-REPORT.json` records those checks. `tokenizer-trace.patch`, `driver.rs`, `compare.py`, `prepared/CASES.json` and `MODEL.json` are the main review surfaces. Native materialization/build commands are intentionally separate from the static checker.
