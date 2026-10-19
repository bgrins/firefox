# Root rlh zoom proof, dependency-effect supplement

Read REPORT.md and the unchanged approved SCOPE.md. `baseline/` is the immutable v1 source closure; `Effects.lean` and the supplemental native/Lean runners add the independently required dependency-state contract.

Authenticate and replay from this directory:

```sh
python3 -I -S verify.py --source-only --expected-freeze DIGEST --lean /absolute/path/to/lean --replay /new/output/path
```

Use the recorded FREEZE.json SHA256 as DIGEST. For a source-only copy, copy every path in SOURCE-MANIFEST.json, plus SOURCE-MANIFEST.json, FILES.json and FREEZE.json, preserving relative paths. Replay requires the pinned local Lean, Rust and C++ toolchains; it uses no live Gecko files or archived generated outputs. `--source-only` without `--replay` checks integrity only. Independent formal review is still required.
