# Numeric lexical and decoded-unit admission

This source-only component verifies the original numeric lexical consumer and its decoded Dimension-unit dependency projection. It retains the arithmetic-loss witnesses. It does not incorporate or accept the later numeric payload repair.

Run from any working directory, with a fresh output path:

```sh
python3 /absolute/path/to/css-tokenizer-numeric-admission-v1/check.py \
  --lean /absolute/path/to/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --output /private/tmp/numeric-admission-clean
```

The checker authenticates its complete manifest and all three parent manifests before importing helpers or executing source. Python 3, the pinned Lean executable and the pinned Rust 1.92.0 toolchain are required. Rust dependencies are included and built directly from source without Cargo/network access. Toolchain installation, compiler runtime/system libraries and Python are external trust dependencies. Paths in the retained Rust toolchain record identify the local pinned compiler; its bytes are checked. No Gecko build or browser is launched.

The replay compiles all 20 Lean modules, audits their reported axioms, extracts 16 complete source definitions, builds actual cssparser and the exact native unit classifier/scanner, compares 81 numeric observations on seven fields, retains nine extra scanner controls, and compiles/discriminates four native and four Lean semantic mutants. Output build products are not companion inputs.

Read REPORT.md and SOURCE-CORRESPONDENCE.md before interpreting results. The original eight obligations remain accounted for individually; full tokenizer, numeric payload fidelity, native representation and whole custom-property graph obligations remain open.
