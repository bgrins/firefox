# Parser observer admission component

Read REPORT.md and SPEC-TRACE.md first. This is a source audit and conditional tracking-history proof; URL-history browser reachability remains open.

Authenticate with `python3 check.py`. Replay from any relocated copy with `python3 check.py --replay /private/tmp/new-empty-output-path`. The destination must not exist. The retained Rust sources/dependencies are complete; only the pinned external Lean and Rust toolchains are required. No Firefox tree/build/browser or network is required by replay.

Lean: `/Users/bgrins/code/firefox/artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean`, SHA256 `d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf`.

TOOLCHAIN.json pins rustc. replay.py prints the exact commands and all subprocess output to its destination. The vendor cssparser parser/tokenizer/rule iterator files equal the retained current source snapshots. Other dependency files retain the authenticated scout closure; this is not a Cargo or Firefox build.
