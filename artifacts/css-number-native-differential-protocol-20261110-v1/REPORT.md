# Native differential protocol source checkpoint

Static source-only replay passes. No Rust compilation, Cargo resolution, native execution, browser test, canonical edit or Git mutation was performed. Native execution is intentionally deferred until root reviews this source/protocol.

The proposal reuses the 81 prior numeric inputs and three prior nonzero-UTF-8 captures, preserving their exact 84-case baseline. Separate augmented histories and narrow threshold/guard cases give 196 planned inputs: 180 fit the proved normalized-ASCII caller domain; 16 retain inherited off-domain inputs as native-only controls. `prepared/` records exact strings, augmented suffixes, byte offsets and ordered JSON-model inputs.

Seven insertion sites extend the existing saved-prefix hook with native digit-loop positions. Reversal preserves the original tokenizer byte-for-byte. The driver distinguishes cached reset from real reparse and requires a progressing suffix token before claiming eviction. `compare.py` binds raw slices to the actual source, compares the seven lexical fields to the pinned decoded-JSON runner, keeps whole-token suffix separate, and checks public-state equivalence across instrumented/uninstrumented and reset paths. Float bits have no mathematical oracle.

Validation completed:

- All Python sources parse; 11 packaged inputs match immutable source hashes.
- 64 future materialization records were independently read from their pinned Git objects by the author; full hashes are retained.
- Corpus and instrumentation patch regenerate exactly.
- Synthetic wire rows parse and preserve the proposed schema.
- Eight synthetic corruptions are refused: sign, integer type, prefix end, extra cached trace, reset end, missing model row, missing cold trace and wrong UTF-8 byte start.
- Arbitrary corresponding float-bit changes remain accepted by the lexical model comparison.
- Source-only replay copied only the 28 hash-bound inputs and left no compiled output.

These are **static/synthetic protocol checks**, not compiled native mutants or real native observations. The Rust driver and tracing patch remain uncompiled. The inherited feature-disabled direct-rustc recipe is prepared; default-feature Cargo dependency resolution/lock and production-feature equivalence remain explicit pending gates in `FEATURE-PLAN.json` and `PROTOCOL.md`.

The native tokenizer pin is the already repaired source, SHA `5319a01e403cd2a93bfc3dd4c53a7e5ec95129360da58c6f9f76f480ae5e6211`, at Firefox `ec467c0219d3d5daf70f42fcc53677cf8a262173`. Historical overflow payload expectations remain archived rather than asserted against the repaired source. This checkpoint does not claim a new bug.

Static reproduction:

```sh
python3 -B artifacts/css-number-native-differential-protocol-20261110-v1/replay.py --out /tmp/css-number-native-protocol-static
```

- Source allowlist SHA-256: `85f92d0dd4674b3bd8f6b16f53b75859cc8511ce05002d0d89edf3c4ca9adadf`
- Static replay receipt SHA-256: `d8c52cb66412d4ce883779da8c1f576d8cf22ff1a4ffbf672e23f0b4f5e44167`

Main review surfaces: `PROTOCOL.md`, `tokenizer-trace.patch`, `driver.rs`, `compare.py`, `prepared/CASES.json`, `MODEL.json` and `FEATURE-PLAN.json`. The next step is source review, followed by a separately authorized native build/execution phase with full logs and fresh owned output directories.
