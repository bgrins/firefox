# Root rlh zoom proof companion

Producer artifact for the approved H2 scope. Final repair: use the already scaled root/direct line-height once. H1 scheduling normalization is separate. Start with [REPORT.md](REPORT.md), [BRIDGE.md](BRIDGE.md), and the unchanged [SCOPE.md](SCOPE.md).

## Verify

Use Python 3.14.6 on the pinned arm64 toolchain. Integrity checks need no browser, Gecko build, repository or network:

```sh
python3 -I artifacts/css-root-rlh-zoom-proof-v1/verify.py
```

A fresh full replay compiles the extracted Rust/C++ capsule and checks Lean; its output directory must not already exist:

```sh
python3 -I artifacts/css-root-rlh-zoom-proof-v1/verify.py \
  --source-only \
  --lean /Users/bgrins/code/firefox/artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --replay /tmp/root-rlh-fresh-replay
```

For a relocated source-only copy, copy every entry of `SOURCE-MANIFEST.json` preserving paths, plus `SOURCE-MANIFEST.json`, `FILES.json`, and `FREEZE.json`. Invoke that copy's `verify.py` with the external pinned Lean path. The verifier authenticates all computational inputs before helper imports and rejects unlisted files. `--freeze-sha HASH` can additionally bind the externally supplied freeze identity. `--source-only` authenticates the required source closure; retained result files are optional and are not used as execution oracles. Full integrity mode authenticates the whole archived capsule.

`TOOLCHAIN.json` pins the Lean dependency closure and compiler entry identities/versions. OS, Python standard library, compiler installations and SDK are external trust requirements; see BRIDGE.md. The native programs are capsule tests, not a Firefox build. No Try or browser is involved.

## Contents

- `Model.lean`, `Trace.lean`, `Grid.lean`: typed providers, source selection, arbitrary finite sequence refinement and exact-grid interpretation.
- `Nonvacuity.lean`, `Admission.lean`, `Mutants.lean`, `Runner.lean`: concrete traces, admission checks and executable semantic mutations.
- `source/`, `candidate/`, `extract.py`, `native/`: complete retained inputs, extraction and declared adapters.
- `oracle.py`, `domain.py`, `check.py`: independent rational/machine-order oracles, exact-domain admission, complete native trace and Lean comparisons.
- `results/`: raw producer observations, extraction/caller ledgers, commands, theorem axioms and summaries. Executables and object caches are regenerated rather than archived.
- `evidence/`: prior independent adjudication and the parent's exact native/WPT gate identity. Browser results are an external parent gate, not produced by this companion.

Independent formal/native-bridge review and the parent's final repair acceptance remain required.
