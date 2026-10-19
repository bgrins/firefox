# Public parser stream scout

Read REPORT.md for claims and boundaries. This is a source-only diagnostic capsule, not a repair or completed formal proof. Browser probes are unexecuted.

Authenticate FREEZE.json and check.py against the handoff hashes before invoking the checker. The checker authenticates every source/helper before compiling or running it:

```sh
python3 artifacts/css-tokenizer-public-stream-scout-v1/check.py --output /tmp/css-public-stream-NEW
```

The output directory must not exist. Compilation uses pinned local Rust and Node executables, no network, Cargo downloads, Firefox build or browser. Complete current cssparser plus its source dependencies is retained. Other retained source files support manual caller review; they are not compiled by the witness. The custom declaration callback is a reduced calc/color facade. Rust compiler/library correctness, normal heap allocation and source text readiness remain premises.

MANIFEST.json lists the closed source/input inventory. FREEZE.json and the manifest are externally anchored in the handoff; they cannot authenticate their own authenticity. development-build/ is historical unsealed scratch and is excluded. Retained evidence/ contains exact witness output and commands; a clean replay recompiles and compares those observations. A relocated copy needs only the manifest-listed files plus MANIFEST.json/FREEZE.json. No imported project Python modules run before authentication.
