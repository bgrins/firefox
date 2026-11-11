# V2 resolution preparation

The v1 execution stopped with Cargo exit 101 before any build. `generate-lockfile --offline` disregarded the seed needed to identify the replaced Git source. The v1 artifact, failure and execution logs are preserved; `origin/` retains their relevant exact bytes.

The sole execution-policy change is to resolve via `cargo metadata --offline` against the seeded lock, validate its actual metadata, and then require a second `cargo metadata --frozen` pass with identical features and unchanged resolved lock. `origin/runner-v2.patch` records the precise runner delta. The baseline, three tokenizer mutations, eight-build structure, comparator, strict model schema, corpus, retained Lean observations, dependency/source/tool pins and failure receipt retention are unchanged.

The actual isolated metadata validation passed. All 437 source files remained pinned; cssparser resolved exactly default/fast_match_byte/fast_match_color. The resolved lock hash is `eb88094dff2b216e2a4a59c35880a787d696c36f800281a4a66cfd1a8f3b2eeb`. No target directory was created, and the temporary workspace was removed. This is Cargo-resolution evidence, not evidence that the native variants compile or that the mutations are detected.

`check.py` remains a separate source-only preparation replay with the same 180 typed rows, 18 schema and four synthetic metadata rejection controls. `resolve.py` is the optional metadata-only replay. `run.py` remains root-owned full execution after review. Default-feature parity is limited to the recorded cssparser feature set; host SDK/linker, whole Gecko build, native refinement and floating-point proof boundaries remain as described in README.md.
