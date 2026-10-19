# Sigma source-only packaging refresh

This capsule repackages the accepted sigma companion for an isolated source-only replay. It does not change the accepted theorem or native repair. The original `css-sigma-proof-v1` capsule remains unchanged.

## Replay

On the accepted macOS arm64 toolchain, use the Lean 4.35.0-rc4 executable whose SHA-256 is recorded in `SOURCE-PROVENANCE.json`. The checker also requires the accepted Apple clang driver hash. The compiler, SDK and Lean distribution are external tools, not vendored inputs.

```sh
python3 -I -S -B check.py --manifest-sha256 MANIFEST_DIGEST \
  --lean /absolute/path/to/lean --output /absolute/path/to/new-output
```

The output must not exist and must be outside this capsule. `--authenticate-only` checks the closed source inventory without compiling. Authentication precedes any imported helper. The checker never reads the repository checkout or an existing Gecko object directory.

## Changes from the original package

- Historical source snapshots replace implicit reads of the live repository. In particular, the complete `nsTextFrame.cpp` snapshot matches the original source manifest, despite later unrelated live edits.
- Complete `ucase.cpp`, its compiled property table, and the compiler-discovered local header closure replace the historical `ucase.o`. The source is compiled with `U_STATIC_IMPLEMENTATION` and `U_COMMON_IMPLEMENTATION`, using C++20 because ICU's included headers use defaulted comparisons. The original probe and helper harness still compile with their unchanged C++17 command.
- The exact original `Sigma.lean`, checker, bridge, helper snapshots, Unicode table and mutation definitions are retained. The wrapper calls their existing functions with explicit snapshot and fresh-object paths. It does not use the original development-mode bypass.
- Every accepted semantic result field is compared with the retained root replay: 16 theorem audits, eight Lean mutations, six diagnostic controls, eight source-identity controls, seven native mutations, five preservation guards, 1,114,112 ICU property answers, and the complete native decision counts.

`source/artifacts/css-sigma-proof-v1/SOURCE-v1.json` and its README are historical provenance. Their old live-file/object requirements are intentionally not the entry point for this refresh. Use this directory's checker and manifest. Generated include aliases, object files, programs, mutation sources and results are written only to the requested output.

## Scope retained

The universal Lean result concerns the finite property-list/context model. Native correspondence exercises the exact helper and call expression with explicit string/style adapters and actual Gecko UTF-16 helpers. ICU Cased/Case_Ignorable answers are checked exhaustively against the retained Unicode 17 table. The complete original native file's other tokens are checked for preservation. Whole `TransformString`, caller scheduling, frame/style ownership, arbitrary C++ executions, other platforms and a performance theorem remain outside the accepted claim. Caller snapshots establish source identity, not a newly proved caller refinement.

This refresh adds reproducible source packaging, not new formal acceptance. Original browser/native acceptance records are retained under `provenance/`. Root must review the refresh before committing it ahead of the separate minimal Gecko/WPT repair.
