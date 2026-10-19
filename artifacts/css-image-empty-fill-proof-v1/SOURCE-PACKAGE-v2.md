# Source-only replay package

This is the portable replay subset of the full local evidence artifact. From the Firefox repository root, run:

```
python3 artifacts/css-image-empty-fill-proof-v1/check.py --out artifacts/css-image-empty-fill-proof-replay
```

The output directory must not already exist. This command regenerates the extracted native fixtures and Lean cases, compiles/runs both implementations and all semantic mutations, and writes fresh receipts. It requires the compiler, SDK and Lean distribution identified by `TOOLCHAIN-v1.json`. Their executable/settings hashes are checked; complete libraries and runtime dependencies are not hermetically captured. No browser, Gecko build or Git operation is performed.

`tooling-paths-v2.txt` contains every file required by `REPLAY-INPUTS-v1.json`, the manifest itself and this document. The complete contents of `SOURCE-v1.json` are included. The replay reads only those local inputs and the explicitly pinned external toolchain. Historical producer outputs are not inputs.

The full local artifact also contains `README.md`, `verify.py`, `FREEZE-v1.json` and producer receipts. Its verifier authenticates that retained historical evidence. Those files are deliberately absent from the source-only package; its entry point is `check.py`, not `verify.py`. The earlier README and tooling list remain unchanged historical evidence and are superseded for packaging by this document and `tooling-paths-v2.txt`.

## Contract and limits

The extracted native boundary includes complete original/candidate painting and preparation functions, operation selection, parameter factories, state defaults, readiness/accessors, iteration and result aggregation. The independent Fraction oracle and rational Lean model compare 9,184 bounded cases; Lean also proves zero-source identities and abstract arbitrary finite fold/dispatch laws. The abstract matrix/result preservation lemmas are record-update facts, not a native refinement theorem.

Frame/style/theme/clip construction, decoded image preparation, sizing/position outputs and nonempty raster alpha are adapters. ClearRect's clipped transparent replacement is a provider contract. Full target origins and six-entry matrix payloads, immediate restoration, later draw arguments and final state are checked in native traces. No decoder, rasterizer, arbitrary integer-overflow or native memory-safety proof is claimed.

The producer passed the complete UBSan/Lean/mutation gate. ASan could not start even an empty program in this environment; a replay reports this limitation explicitly and does not credit an ASan corpus run. Named lifetime owners and a specific Clang lifetimebound negative diagnostic supplement source review. If ASan starts on the replay host, the full instrumented corpus and negative lifetime control are required to execute. Full-artifact receipts and independent review remain available locally but are not claimed to accompany this source-only subset.
