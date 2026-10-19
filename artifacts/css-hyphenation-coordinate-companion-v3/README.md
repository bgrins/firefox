# Narrow measurement-coordinate companion

The repair changes one comparison in `gfxTextRun::BreakAndMeasureText` from an absolute word boundary versus a relative buffer length to an absolute boundary versus the current buffer range start. Its separate native commit contains only that change and `hyphenation-text-run-offset.html`. This companion preserves the original complete ownership scope and its counterexamples.

## What is reproduced

The unchanged, authenticated `baseline/` capsule regenerates complete TransformText, skip mapping, GetHyphenationBreaks, classification and BreakAndMeasureText, followed by the complete advance/ligature and spacing provider extensions. It replays its original fixed controls and whole model. The wrapper then binds the entire measurement method to the exact root browser original/candidate snapshots, substitutes only the comparison in two freshly generated headers, compiles the candidates and compares both source variants on the same 16 retained target/control inputs and 40,608 controls. Both the initial provider facade and the full spacing extension must reproduce the exact retained outputs. The oracle additionally requires translation-paired candidate measurement outputs to agree and the two target pairs to select the natural boundary at 21. The native output includes fit, used hyphenation, last break, priority and metric advance; no output field is discarded from preservation checks.

`guard/` independently kernel-checks 31 modules / 289 reports, including ten new theorems deriving the comparison relation from constructor-reachable storage and full modeled provider lengths. Its reachability closure conservatively admits more guarded transition sequences than the exact loop. This is not a universal native compiler/heap or whole-loop translation proof.

The 16 inputs and retained range observations are fixtures: their historical generator was not retained, as confirmed by the producer. This wrapper does not regenerate dictionary masks. It authenticates their provenance and reproduces the measurement experiment from source. `browser/` retains the exact paired real-browser evidence: two new failures become passes, all eight new cases pass, and 19 existing passes plus one metadata expected failure are unchanged. The WPT independently compares identical suffix geometry after a calibrated whole-line prefix, with automatic/manual/none and conditional-hyphen controls; it does not assume a particular dictionary's break list.

## Relocation correction

Version 1 authenticated correctly but its first root replay failed before native compilation: Lean inherited the repository working directory while its input was relocated under /private/tmp. Version 2 sets each subprocess working directory explicitly. The baseline checker and its nested consumer/driver inherit the copied baseline root; both their source and generated Lean inputs are inside it. The guard is copied beside its output, and runs under their common output parent. All paths are resolved before changing directories. Source/proof/native fixtures, nested checkers and expected outputs are unchanged. The original failed receipt remains separate.

## Replay

From this directory, use the trusted digest in the parent handoff (or independently authenticated FREEZE.json):

```sh
python3 -I -S -B check.py --manifest-sha TRUSTED_DIGEST --lean /absolute/path/to/lean --output /new/output
```

`--authenticate-only` validates the entire source closure and exact native delta without compiling. The output directory must not exist and must be outside this capsule. All imported code is authenticated before execution; the baseline is copied into the output before producing generated files. Nothing reads mutable Firefox source or an old development binary. No network or browser is required. The manifest lists every input; `MANIFEST.json` and `FREEZE.json` are the only additional package files.

Dependencies: Python 3 standard library; pinned Lean 4.35.0-rc4 Darwin arm64 executable (SHA d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf and its installed standard library); pinned Apple Clang 17 executable (SHA be5518e9c6736cda8dfc3486ce11e8112a2e08045084260691cf41f57a653f59), Xcode macOS SDK/libc++ and system libicucore. The existing bridge identifies system ICU 78.1 as a foreign Unicode provider, not Firefox's bundled ICU refinement. No Rust toolchain or generated object/library is a package input. Native recompilation uses UBSan.

## Acceptance boundary

Recommend accepting the narrow coordinate repair after a fresh complete replay of this wrapper succeeds and root records that result. The paired browser/source/oracle review and model guard admission pass. This newly assembled native wrapper has not been executed by the independent reviewer because the task prohibits native builds; its source authentication has passed. Do not convert that pending replay into a completed gate.

Actual native array/capacity/uint32 semantics, persistent query/cache association, DOM/style reconstruction, all font/shaping and numeric semantics remain explicit trusted or open boundaries as recorded by the original approved scope. The full ownership dossier is not accepted by this recommendation. Frozen LF/nowrap/Ahom and filter completeness counterexamples remain valid statements about their original sources. Neither this package nor its two-file patch includes those repairs.


## Version 3 extraction paths

Root's relocated v2 run passed the complete baseline native/model replay and
the guard kernel replay, then stopped before candidate compilation because the
extractor records paths relative to its consumer source tree. This version
copies the two authenticated complete source snapshots into the freshly built
consumer's development directory before extraction. Source bytes, complete
method comparison, compiler commands, fixtures and expected outputs are
unchanged. Original v1/v2 capsules and root failure receipts are preserved.
